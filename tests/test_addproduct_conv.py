import sys
from pathlib import Path
import types
import asyncio
import os
import pytest

os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("ADMIN_PHONE", "+111")
os.environ.setdefault("FERNET_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")

pytest.importorskip("telegram")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import (  # noqa: E402
    addproduct_start_conv,
    addproduct_pid,
    addproduct_price,
    addproduct_username,
    addproduct_password,
    addproduct_secret,
    addproduct_name,
    ADD_PID,
    ADD_PRICE,
    ADD_USERNAME,
    ADD_PASSWORD,
    ADD_SECRET,
    ADD_NAME,
    data,
    ADMIN_ID,
)
from telegram.ext import ConversationHandler
from botlib.translations import tr


class DummyBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, uid, text):
        self.sent.append((uid, text))


class DummyCallbackUpdate:
    def __init__(self, user_id, data_str):
        self.replies = []

        async def reply(text, reply_markup=None):
            self.replies.append((text, reply_markup))

        async def answer():
            pass

        self.callback_query = types.SimpleNamespace(
            data=data_str,
            message=types.SimpleNamespace(reply_text=reply),
            from_user=types.SimpleNamespace(id=user_id),
            answer=answer,
        )
        self.effective_user = self.callback_query.from_user
        self.message = None


class DummyMessageUpdate:
    def __init__(self, user_id, text=""):
        self.replies = []

        async def reply(text, reply_markup=None):
            self.replies.append((text, reply_markup))

        self.message = types.SimpleNamespace(
            from_user=types.SimpleNamespace(id=user_id),
            reply_text=reply,
            text=text,
        )
        self.effective_user = self.message.from_user


class DummyContext:
    def __init__(self):
        self.args = []
        self.user_data = {}
        self.bot = DummyBot()


def test_addproduct_conversation_flow(tmp_path):
    data['products'] = {}
    update = DummyCallbackUpdate(ADMIN_ID, 'adminmenu:addproduct')
    context = DummyContext()
    context.user_data['lang'] = 'en'
    state = asyncio.run(addproduct_start_conv(update, context))
    assert state == ADD_PID

    update1 = DummyMessageUpdate(ADMIN_ID, 'p42')
    state = asyncio.run(addproduct_pid(update1, context))
    assert state == ADD_PRICE

    update2 = DummyMessageUpdate(ADMIN_ID, '9.99')
    state = asyncio.run(addproduct_price(update2, context))
    assert state == ADD_USERNAME

    update3 = DummyMessageUpdate(ADMIN_ID, 'user')
    state = asyncio.run(addproduct_username(update3, context))
    assert state == ADD_PASSWORD

    update4 = DummyMessageUpdate(ADMIN_ID, 'pass')
    state = asyncio.run(addproduct_password(update4, context))
    assert state == ADD_SECRET

    update5 = DummyMessageUpdate(ADMIN_ID, 'secret')
    state = asyncio.run(addproduct_secret(update5, context))
    assert state == ADD_NAME

    update6 = DummyMessageUpdate(ADMIN_ID, 'Nice')
    state = asyncio.run(addproduct_name(update6, context))
    assert state == ConversationHandler.END
    assert 'p42' in data['products']
    assert data['products']['p42']['price'] == '9.99'

