import sys
from pathlib import Path
import importlib
import os
import pytest

# Required env vars so bot imports successfully
os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("ADMIN_PHONE", "+111")
os.environ.setdefault("FERNET_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")

pytest.importorskip("telegram")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_data_file_env(monkeypatch, tmp_path):
    custom = tmp_path / "custom.json"
    monkeypatch.setenv("DATA_FILE", str(custom))
    if "bot" in sys.modules:
        del sys.modules["bot"]
    bot = importlib.import_module("bot")
    assert bot.DATA_FILE == custom
    assert bot.storage.path == custom
