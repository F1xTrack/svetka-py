import pytest
import os
from core.config import ConfigManager

@pytest.fixture
def temp_config():
    path = "test_config_pytest.yaml"
    if os.path.exists(path):
        os.remove(path)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_config_generation(temp_config):
    cm = ConfigManager(temp_config)
    assert os.path.exists(temp_config)
    assert cm.get("vision.enabled") is True
    assert cm.get("personality.name") == "Svetka"

def test_config_get_nested(temp_config):
    cm = ConfigManager(temp_config)
    assert cm.get("vision.fps") == 5
    assert cm.get("non_existent.key", "default") == "default"

def test_config_save(temp_config):
    cm = ConfigManager(temp_config)
    cm.config["vision"]["fps"] = 10
    cm.save_config()
    
    cm2 = ConfigManager(temp_config)
    assert cm2.get("vision.fps") == 10
