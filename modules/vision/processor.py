import asyncio
import os
import time
from pathlib import Path
import cv2
import mss
import numpy as np
import win32gui
from PyQt6.QtCore import QObject, pyqtSignal
from core.config import ConfigManager


class VisionProcessor(QObject):
    """
    Основной класс для захвата и обработки изображения с экрана.
    """
    # Сигнал при получении нового кадра (в формате numpy/cv2)
    frame_captured = pyqtSignal(np.ndarray)
    # Сигнал при обнаружении существенного изменения
    change_detected = pyqtSignal(np.ndarray, float)
    # Сигнал для запроса анализа (по таймеру)
    analysis_requested = pyqtSignal(np.ndarray)
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.cm = config_manager
        self.sct = mss.mss()
        self.is_running = False
        self._task = None
        self.last_frame = None
        self.video_writer = None
        self.is_recording = False
        
        # Настройки из конфига
        self.fps = self.cm.get("vision.fps", 5)
        self.capture_region = self.cm.get("vision.capture_region", [0, 0, 1920, 1080])
        self.cache_dir = Path("cache/vision")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройки обработки
        self.max_resolution = self.cm.get("vision.max_resolution", [1280, 720])
        self.contrast = self.cm.get("vision.contrast", 1.0)
        self.brightness = self.cm.get("vision.brightness", 1.0)
        self.threshold = self.cm.get("vision.threshold", 0.05) # Порог MSE
        self.blur_zones = self.cm.get("privacy.blur_zones", [])
        self.blacklist = self.cm.get("privacy.blacklist", [])
        self.process_interval = self.cm.get("vision.process_interval", 5.0)
        self._last_analysis_time = 0

    def _is_blacklisted_active(self) -> bool:
        """Проверяет, активно ли окно из черного списка."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd).lower()
            for pattern in self.blacklist:
                if pattern.lower() in title:
                    return True
        except Exception as e:
            print(f"Error checking active window: {e}")
        return False

    def _get_monitor(self):
        """Преобразует capture_region [x, y, w, h] в формат mss."""
        x, y, w, h = self.capture_region
        return {"top": y, "left": x, "width": w, "height": h}

    async def start(self):
        """Запускает цикл захвата экрана."""
        if self.is_running:
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._capture_loop())
        print("VisionProcessor started.")

    async def stop(self):
        """Останавливает цикл захвата экрана."""
        self.is_running = False
        if self._task:
            await self._task
        self.stop_recording()
        print("VisionProcessor stopped.")

    async def _capture_loop(self):
        """Внутренний цикл захвата."""
        interval = 1.0 / self.fps
        
        while self.is_running:
            start_time = time.perf_counter()
            
            try:
                # Проверка черного списка
                if self._is_blacklisted_active():
                    # Можно эмитить пустой кадр или просто ждать
                    pass
                else:
                    # Захват экрана
                    monitor = self._get_monitor()
                    screenshot = self.sct.grab(monitor)
                    
                    # Конвертация в numpy array (BGRA -> BGR)
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Обработка кадра
                    processed_frame = self._process_frame(frame)
                    
                    # Детекция изменений
                    if self.last_frame is not None:
                        mse = self._calculate_mse(self.last_frame, processed_frame)
                        if mse > self.threshold:
                            self.change_detected.emit(processed_frame, mse)
                    
                    self.last_frame = processed_frame.copy()
                    
                    # Эмиссия сигнала
                    self.frame_captured.emit(processed_frame)
                    
                    # Запрос анализа по интервалу
                    now = time.time()
                    if now - self._last_analysis_time >= self.process_interval:
                        self.analysis_requested.emit(processed_frame)
                        self._last_analysis_time = now
                    
                    # Запись видео, если активно
                    if self.is_recording and self.video_writer:
                        self.video_writer.write(processed_frame)
                
            except Exception as e:
                print(f"Error in VisionProcessor loop: {e}")
            
            # Ожидание следующего кадра
            elapsed = time.perf_counter() - start_time
            await asyncio.sleep(max(0, interval - elapsed))

    def start_recording(self, filename: str = None) -> str:
        """Зачинает запись видео."""
        if self.is_recording:
            return None
            
        if filename is None:
            filename = f"clip_{int(time.time())}.webm"
        
        path = self.cache_dir / filename
        
        # Кодек для webm
        fourcc = cv2.VideoWriter_fourcc(*'VP80')
        w, h = self.max_resolution
        self.video_writer = cv2.VideoWriter(str(path), fourcc, self.fps, (w, h))
        self.is_recording = True
        return str(path)

    def stop_recording(self):
        """Останавливает запись видео."""
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def _calculate_mse(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Вычисляет среднеквадратичную ошибку между двумя кадрами."""
        if frame1.shape != frame2.shape:
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
        
        err = np.sum((frame1.astype("float") - frame2.astype("float")) ** 2)
        err /= float(frame1.shape[0] * frame1.shape[1] * 255 * 255) # Нормализация
        return err

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Ресайз, яркость, контрастность."""
        # Ресайз
        target_w, target_h = self.max_resolution
        h, w = frame.shape[:2]
        if w > target_w or h > target_h:
            frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        # Яркость и контрастность
        if self.brightness != 1.0 or self.contrast != 1.0:
            frame = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=(self.brightness - 1.0) * 127)
        
        # Наложение Blur-зон
        for zone in self.blur_zones:
            try:
                x, y, w, h = zone
                # Масштабируем зону под текущий размер кадра, если нужно
                orig_w, orig_h = self.capture_region[2:]
                curr_h, curr_w = frame.shape[:2]
                
                rx, ry = curr_w / orig_w, curr_h / orig_h
                nx, ny, nw, nh = int(x * rx), int(y * ry), int(w * rx), int(h * ry)
                
                sub = frame[ny:ny+nh, nx:nx+nw]
                if sub.size > 0:
                    # Размытие (ядро должно быть нечетным)
                    ksize = max(3, (int(nw / 10) // 2 * 2 + 1))
                    sub = cv2.GaussianBlur(sub, (ksize, ksize), 0)
                    frame[ny:ny+nh, nx:nx+nw] = sub
            except Exception as e:
                print(f"Error applying blur zone {zone}: {e}")
            
        return frame

    def save_frame(self, frame: np.ndarray, name: str = None) -> str:
        """Сохраняет кадр во временную папку."""
        if name is None:
            name = f"shot_{int(time.time())}.png"
        
        path = self.cache_dir / name
        cv2.imwrite(str(path), frame)
        return str(path)
