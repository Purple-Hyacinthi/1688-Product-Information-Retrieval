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

def test_update_section():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        
        config.update_section("test_section", {"key1": "value1", "key2": "value2"})
        loaded = config.load_config()
        assert loaded["test_section"]["key1"] == "value1"
        assert loaded["test_section"]["key2"] == "value2"
        
        config.update_section("test_section", {"key1": "updated"})
        loaded = config.load_config()
        assert loaded["test_section"]["key1"] == "updated"
        assert loaded["test_section"]["key2"] == "value2"

def test_get():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = ConfigManager(config_path)
        
        config.save_config({"section": {"key": "value"}})
        assert config.get("section", "key") == "value"
        assert config.get("section", "nonexistent") is None
        assert config.get("section", "nonexistent", "default") == "default"
        assert config.get("nonexistent", "key") is None
        assert config.get("nonexistent", "key", "default") == "default"