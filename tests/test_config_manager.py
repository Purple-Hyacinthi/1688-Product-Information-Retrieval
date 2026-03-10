# tests/test_config_manager.py
import os
import json
import tempfile
import pytest
from src.config_manager import ConfigManager

def test_config_manager_creation():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        assert config.config_path == config_path

def test_load_default_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        default_config = config.load_config()
        assert "1688_api" in default_config
        assert "llm" in default_config

def test_save_and_load_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        
        test_data = {"test": "value"}
        config.save_config(test_data)
        
        loaded = config.load_config()
        assert loaded["test"] == "value"