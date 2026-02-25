import asyncio
import logging
import sounddevice as sd
import numpy as np
import edge_tts
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from core.config import ConfigManager

logger = logging.getLogger(__name__)

class AudioProcessor(QObject):
    volume_changed = pyqtSignal(float) # Signal for UI (0.0 to 1.0)
    voice_detected = pyqtSignal(np.ndarray) # Signal for Brain (raw audio data)
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config = config_manager
        self.is_running = False
        
        # Load settings from config
        self.sample_rate = self.config.get("audio.sample_rate", 16000)
        self.channels = self.config.get("audio.channels", 1)
        self.mic_enabled = self.config.get("audio.mic_enabled", True)
        self.mic_index = self.config.get("audio.mic_index", -1)
        self.system_audio_enabled = self.config.get("audio.system_audio_enabled", False)
        
        # TTS settings
        self.tts_voice = self.config.get("audio.tts_voice", "ru-RU-SvetlanaNeural")
        self.tts_rate = self.config.get("audio.tts_rate", "+0%")
        self.tts_volume = self.config.get("audio.tts_volume", "+0%")
        self.tts_pitch = self.config.get("audio.tts_pitch", "+0Hz")
        
        # Audio Buffer (10 seconds by default)
        self._buffer_duration = 10 
        self._max_buffer_size = self.sample_rate * self._buffer_duration
        self._audio_buffer = np.zeros(self._max_buffer_size, dtype=np.float32)
        
        self._mic_stream: Optional[sd.InputStream] = None
        self._system_stream: Optional[sd.InputStream] = None
        self._capture_task: Optional[asyncio.Task] = None

    def _get_wasapi_loopback_device(self):
        """Finds the default WASAPI loopback device."""
        try:
            devices = sd.query_devices()
            wasapi = sd.query_hostapis(name='Windows WASAPI')
            default_out_id = sd.default.device[1]
            if default_out_id == -1:
                return None
                
            default_out_name = sd.query_devices(default_out_id)['name']
            
            for i in range(len(devices)):
                if devices[i]['hostapi'] == wasapi['index'] and \
                   devices[i]['max_input_channels'] > 0 and \
                   default_out_name in devices[i]['name']:
                    return i
        except Exception as e:
            logger.debug(f"WASAPI loopback search failed: {e}")
        return None

    async def start(self):
        """Starts audio capture."""
        if self.is_running:
            return
            
        logger.info("Starting AudioProcessor...")
        self.is_running = True
        
        # Microphone capture
        if self.mic_enabled:
            try:
                device = self.mic_index if self.mic_index != -1 else None
                self._mic_stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    device=device,
                    callback=self._audio_callback
                )
                self._mic_stream.start()
                logger.info(f"Microphone capture started (device: {device})")
            except Exception as e:
                logger.error(f"Failed to start microphone capture: {e}")

        # System audio capture (Loopback)
        if self.config.get("audio.system_audio_enabled", False):
            try:
                loopback_id = self._get_wasapi_loopback_device()
                if loopback_id is not None:
                    self._system_stream = sd.InputStream(
                        samplerate=self.sample_rate,
                        channels=self.channels,
                        device=loopback_id,
                        callback=self._system_audio_callback
                    )
                    self._system_stream.start()
                    logger.info(f"System audio loopback started (device: {loopback_id})")
                else:
                    logger.warning("WASAPI loopback device not found")
            except Exception as e:
                logger.error(f"Failed to start system audio capture: {e}")
        
        # Placeholder for capture loop
        self._capture_task = asyncio.create_task(self._capture_loop())

    def _audio_callback(self, indata, frames, time, status):
        """Callback for microphone data."""
        if status:
            logger.warning(f"Mic status: {status}")
        
        audio = indata[:, 0].copy()
        
        # 1. Noise reduction (optional)
        if self.config.get("audio.noise_cancellation", True):
            audio = self._reduce_noise(audio)
            
        # 2. Calculate volume and emit for UI
        vol = self._calculate_volume(audio)
        self.volume_changed.emit(vol)
        
        # 3. Add to ring buffer
        self._add_to_buffer(audio)
        
        # 4. Voice Activity Detection
        threshold = self.config.get("audio.volume_threshold", 0.01)
        if vol > threshold:
            # For simplicity, we just emit a signal when threshold is crossed.
            # In a full implementation, we might accumulate a phrase before emitting.
            self.voice_detected.emit(audio)

    def _system_audio_callback(self, indata, frames, time, status):
        """Callback for system audio data."""
        if status:
            logger.warning(f"System audio status: {status}")
        # Process indata
        pass

    def _mix_audio(self, *buffers: np.ndarray) -> np.ndarray:
        """Mixes multiple audio buffers into one."""
        if not buffers:
            return np.array([], dtype=np.float32)
            
        # Ensure all buffers have the same shape (pad with zeros if necessary)
        max_len = max(len(b) for b in buffers)
        standardized_buffers = []
        for b in buffers:
            if len(b) < max_len:
                b = np.pad(b, (0, max_len - len(b)), 'constant')
            standardized_buffers.append(b)
            
        # Sum and clip to [-1.0, 1.0]
        mixed = np.sum(standardized_buffers, axis=0)
        return np.clip(mixed, -1.0, 1.0)

    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """Basic noise reduction using spectral thresholding."""
        if not self.config.get("audio.noise_cancellation", True):
            return audio
            
        # Compute FFT
        fft = np.fft.rfft(audio)
        magnitudes = np.abs(fft)
        phases = np.angle(fft)
        
        # Simple noise floor estimation (mean of lower magnitudes)
        threshold = np.mean(magnitudes) * 0.5
        
        # Zero out magnitudes below threshold
        magnitudes[magnitudes < threshold] = 0
        
        # Reconstruct FFT and inverse
        fft_clean = magnitudes * np.exp(1j * phases)
        return np.fft.irfft(fft_clean, n=len(audio))

    def _calculate_volume(self, audio: np.ndarray) -> float:
        """Calculates the RMS volume of the audio buffer."""
        if len(audio) == 0:
            return 0.0
        rms = np.sqrt(np.mean(audio**2))
        return float(np.clip(rms, 0.0, 1.0))

    def _add_to_buffer(self, data: np.ndarray):
        """Adds new audio data to the ring buffer."""
        if len(data) == 0:
            return
            
        if len(data) >= self._max_buffer_size:
            self._audio_buffer = data[-self._max_buffer_size:].copy()
        else:
            # Shift buffer to the left and add new data to the right
            self._audio_buffer = np.roll(self._audio_buffer, -len(data))
            self._audio_buffer[-len(data):] = data

    def get_recent_audio(self, duration_samples: Optional[int] = None) -> np.ndarray:
        """Returns the most recent audio from the buffer."""
        if duration_samples is None or duration_samples >= self._max_buffer_size:
            return self._audio_buffer.copy()
        return self._audio_buffer[-duration_samples:].copy()

    async def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribes audio data using the configured STT provider."""
        if len(audio_data) == 0:
            return ""
            
        logger.info("Transcribing audio...")
        # Placeholder for actual API call. 
        # In the future, this will use an APIBridge to call OpenAI/Gemini Whisper endpoint.
        await asyncio.sleep(0.1) # Simulate network delay
        return "Transcribed text placeholder"

    async def speak(self, text: str, output_path: str) -> str:
        """Synthesizes speech from text and saves to a file."""
        if not text:
            return ""
            
        logger.info(f"Synthesizing speech: {text[:20]}...")
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.tts_voice,
                rate=self.tts_rate,
                volume=self.tts_volume,
                pitch=self.tts_pitch
            )
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return ""

    async def stop(self):
        """Stops audio capture."""
        if not self.is_running:
            return
            
        logger.info("Stopping AudioProcessor...")
        self.is_running = False
        
        if self._mic_stream:
            self._mic_stream.stop()
            self._mic_stream.close()
            self._mic_stream = None
            
        if self._system_stream:
            self._system_stream.stop()
            self._system_stream.close()
            self._system_stream = None
            
        if self._capture_task:
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass
            self._capture_task = None

    async def _capture_loop(self):
        """Main loop for audio capture."""
        try:
            while self.is_running:
                # Placeholder for actual data capture
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in audio capture loop: {e}")
            self.is_running = False
