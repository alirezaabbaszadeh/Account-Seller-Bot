import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import get_bot_token  # noqa: E402


def test_get_bot_token_argument():
    assert get_bot_token("cli") == "cli"


def test_get_bot_token_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "env")
    assert get_bot_token(None) == "env"


def test_get_bot_token_missing(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        get_bot_token(None)
