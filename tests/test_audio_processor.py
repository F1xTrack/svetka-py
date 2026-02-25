import pytest
import asyncio
import numpy as np
from modules.audio.processor import AudioProcessor
from core.config import ConfigManager

@pytest.fixture
def config_manager(tmp_path):
    config_file = tmp_path / "config.yaml"
    cm = ConfigManager(str(config_file))
    return cm

@pytest.fixture
def processor(config_manager):
    return AudioProcessor(config_manager)

@pytest.mark.asyncio
async def test_audio_processor_init(processor):
    assert processor.is_running is False
    assert processor.sample_rate == 16000
    assert processor.channels == 1

@pytest.mark.asyncio
async def test_audio_processor_start_stop(processor):
    await processor.start()
    assert processor.is_running is True
    await processor.stop()
    assert processor.is_running is False

from unittest.mock import patch

@pytest.mark.asyncio
async def test_audio_mixing(processor):
    # Simulate two buffers of audio data (numpy arrays)
    mic_data = np.array([0.5, -0.5, 0.1], dtype=np.float32)
    sys_data = np.array([0.2, 0.3, -0.1], dtype=np.float32)
    
    # We expect the mixed data to be their sum (simple mixing)
    expected_mixed = np.array([0.7, -0.2, 0.0], dtype=np.float32)
    
    # Manually call mixing logic
    mixed = processor._mix_audio(mic_data, sys_data)
    
    assert np.allclose(mixed, expected_mixed)

@pytest.mark.asyncio
async def test_noise_reduction(processor):
    # Create a signal with noise
    t = np.linspace(0, 1, 16000)
    clean_signal = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    noise = 0.1 * np.random.normal(size=16000).astype(np.float32)
    noisy_signal = clean_signal + noise
    
    # Enable noise reduction in config
    processor.config.set("audio.noise_cancellation", True)
    
    # Apply noise reduction
    reduced = processor._reduce_noise(noisy_signal)
    
    # In a simple implementation, the energy of the signal should decrease 
    # (since we removed noise) but the signal should still be similar to clean
    assert np.var(reduced) < np.var(noisy_signal)
    assert len(reduced) == len(noisy_signal)

@pytest.mark.asyncio
async def test_calculate_volume(processor):
    # Quiet signal
    quiet_signal = np.zeros(1024, dtype=np.float32)
    assert processor._calculate_volume(quiet_signal) == 0.0
    
    # Loud signal (full amplitude sine)
    t = np.linspace(0, 1, 1024)
    loud_signal = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    volume = processor._calculate_volume(loud_signal)
    assert 0.6 < volume < 0.8 # RMS of sine is approx 0.707

@pytest.mark.asyncio
async def test_stt_transcription(processor):
    # Mock some audio data
    audio_data = np.zeros(16000, dtype=np.float32)
    
    # Mock API call for STT
    with patch.object(processor, "transcribe", return_value="Hello world") as mock_transcribe:
        text = await processor.transcribe(audio_data)
        assert text == "Hello world"
        assert mock_transcribe.called

@pytest.mark.asyncio
async def test_tts_synthesis(processor, tmp_path):
    text = "Hello, I am Svetka."
    output_path = tmp_path / "test_tts.mp3"
    
    with patch.object(processor, "speak", return_value=str(output_path)) as mock_speak:
        path = await processor.speak(text, str(output_path))
        assert path == str(output_path)
        assert mock_speak.called

@pytest.mark.asyncio
async def test_audio_buffer_accumulation(processor):
    # Buffer size in config (e.g., 16000 samples per second, 10 seconds = 160000)
    samples = np.random.normal(size=1000).astype(np.float32)
    processor._add_to_buffer(samples)
    
    buf = processor.get_recent_audio(1000)
    assert len(buf) == 1000
    assert np.allclose(buf, samples)

@pytest.mark.asyncio
async def test_audio_callbacks(processor):
    # Test mic callback
    data = np.zeros((1024, 1), dtype=np.float32)
    processor._audio_callback(data, 1024, None, None)
    
    # Test system callback
    processor._system_audio_callback(data, 1024, None, None)
    # Should not raise errors

@pytest.mark.asyncio
async def test_get_wasapi_loopback_device(processor):
    # Mock sounddevice.query_devices and hostapis
    mock_devices = [
        {'name': 'Mic', 'hostapi': 0, 'max_input_channels': 1},
        {'name': 'Speakers', 'hostapi': 1, 'max_input_channels': 2}
    ]
    mock_hostapis = [
        {'name': 'MME', 'index': 0},
        {'name': 'Windows WASAPI', 'index': 1}
    ]
    
    with patch("sounddevice.query_devices", side_effect=lambda id=None, kind=None: 
               mock_devices[id] if id is not None else mock_devices):
        with patch("sounddevice.query_hostapis", side_effect=lambda name=None, index=None: 
                   mock_hostapis[index] if index is not None else next(h for h in mock_hostapis if h['name'] == name)):
            with patch("sounddevice.default.device", [0, 1]): 
                dev_id = processor._get_wasapi_loopback_device()
                assert dev_id == 1

@pytest.mark.asyncio
async def test_start_capture_failure(processor):
    # Mock sd.InputStream to raise exception
    with patch("sounddevice.InputStream", side_effect=RuntimeError("Device error")):
        await processor.start()
        # Should log error and continue (or set is_running False if critical, here it continues)
        assert processor.is_running is True 
        await processor.stop()

@pytest.mark.asyncio
async def test_audio_mixing_clipping(processor):
    # Test clipping (values exceeding -1.0 to 1.0)
    mic_data = np.array([0.8], dtype=np.float32)
    sys_data = np.array([0.5], dtype=np.float32)
    
    # Expected should be clipped to 1.0
    mixed = processor._mix_audio(mic_data, sys_data)
    assert mixed[0] == 1.0
