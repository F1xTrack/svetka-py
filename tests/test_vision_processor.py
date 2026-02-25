import pytest
import asyncio
import numpy as np
import os
from pathlib import Path
from modules.vision.processor import VisionProcessor
from core.config import ConfigManager

@pytest.fixture
def config_manager(tmp_path):
    config_file = tmp_path / "config.yaml"
    cm = ConfigManager(str(config_file))
    return cm

@pytest.fixture
def processor(config_manager):
    return VisionProcessor(config_manager)

@pytest.mark.asyncio
async def test_processor_init(processor):
    assert processor.is_running is False
    assert processor.fps == 5
    assert processor.cache_dir.exists()

@pytest.mark.asyncio
async def test_capture_loop_start_stop(processor):
    await processor.start()
    assert processor.is_running is True
    await asyncio.sleep(0.5)
    await processor.stop()
    assert processor.is_running is False

@pytest.mark.asyncio
async def test_process_frame_resizing(processor):
    processor.max_resolution = [100, 100]
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    processed = processor._process_frame(frame)
    assert processed.shape == (100, 100, 3)

@pytest.mark.asyncio
async def test_mse_calculation(processor):
    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    mse = processor._calculate_mse(frame1, frame2)
    assert mse == 1.0
    
    mse_same = processor._calculate_mse(frame1, frame1)
    assert mse_same == 0.0

@pytest.mark.asyncio
async def test_blur_application(processor):
    processor.blur_zones = [[10, 10, 20, 20]]
    processor.capture_region = [0, 0, 100, 100]
    processor.max_resolution = [100, 100]
    
    # Create a frame with a white square
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[10:30, 10:30] = 255
    
    processed = processor._process_frame(frame)
    # The blurred area should not be pure white anymore
    assert not np.all(processed[15:25, 15:25] == 255)

@pytest.mark.asyncio
async def test_recording(processor, tmp_path):
    processor.cache_dir = tmp_path
    processor.max_resolution = [160, 120]
    path = processor.start_recording("test.webm")
    assert processor.is_recording is True
    
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    processor.video_writer.write(frame)
    
    processor.stop_recording()
    assert processor.is_recording is False
    assert os.path.exists(path)
