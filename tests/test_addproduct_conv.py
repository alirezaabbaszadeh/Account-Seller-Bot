import sys
from pathlib import Path
import types
import asyncio
import os
import pytest

# Required env vars for bot import
os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("ADMIN_PHONE", "+111")
os.environ.setdefault("FERNET_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")

pytest.importorskip("telegram")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot_conversations import (
    addproduct_menu,
    addproduct_cancel,
    ASK_ID,
)
from bot import ADMIN_ID
from botlib.translations import tr
from telegram.ext import ConversationHandler


class DummyUpdate:
    def __init__(self, user_id):
        self.message = types.SimpleNamespace(
            from_user=types.SimpleNamespace(id=user_id),
            reply_text=self._reply,
            text="",
        )
        self.effective_user = self.message.from_user
        self.replies = []

    async def _reply(self, text, reply_markup=None):
        self.replies.append(text)


class DummyContext:
    def __init__(self):
        self.args = []
        self.user_data = {}


def test_back_button_cancels_and_clears():
    context = DummyContext()
    update = DummyUpdate(ADMIN_ID)

    state = asyncio.run(addproduct_menu(update, context))
    assert state == ASK_ID

    lang = context.user_data["lang"]
    update.message.text = tr("back_button", lang)
    state = asyncio.run(addproduct_cancel(update, context))

    assert state == ConversationHandler.END
    assert "new_product" not in context.user_data
    assert update.replies[-1] == tr("operation_cancelled", lang)
