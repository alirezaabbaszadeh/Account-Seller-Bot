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
    admin_callback,
    admin_menu_callback,
    menu_callback,
    start,
    addproduct,
    data,
    ADMIN_ID,
)
from botlib.translations import tr  # noqa: E402


class DummyBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, uid, text):
        self.sent.append((uid, text))


class DummyCallbackUpdate:
    def __init__(self, user_id, data):
        self.replies = []

        async def reply(text, reply_markup=None):
            self.replies.append((text, reply_markup))

        async def answer():
            pass

        self.callback_query = types.SimpleNamespace(
            data=data,
            message=types.SimpleNamespace(reply_text=reply),
            from_user=types.SimpleNamespace(id=user_id),
            answer=answer,
        )
        self.effective_user = self.callback_query.from_user
        self.message = None


class DummyContext:
    def __init__(self):
        self.args = []
        self.user_data = {}
        self.bot = DummyBot()


class DummyMessageUpdate:
    def __init__(self, user_id):
        self.replies = []

        async def reply(text, reply_markup=None):
            self.replies.append((text, reply_markup))

        self.message = types.SimpleNamespace(
            from_user=types.SimpleNamespace(id=user_id),
            reply_text=reply,
        )
        self.effective_user = self.message.from_user


def test_admin_pending_list():
    data['pending'] = [{'user_id': 2, 'product_id': 'p1', 'file_id': 'f'}]
    update = DummyCallbackUpdate(ADMIN_ID, 'admin:pending')
    context = DummyContext()
    asyncio.run(admin_callback(update, context))
    text, markup = update.replies[0]
    assert tr('pending_entry', 'en').format(user_id=2, product_id='p1') == text
    assert markup.inline_keyboard[0][0].text == tr('approve_button', 'en')


def test_admin_callback_approve():
    data['pending'] = [{'user_id': 2, 'product_id': 'p1', 'file_id': 'f'}]
    data['products'] = {'p1': {'price': '1', 'username': 'u', 'password': 'p', 'secret': 's', 'buyers': []}}
    update = DummyCallbackUpdate(ADMIN_ID, 'admin:approve:2:p1')
    context = DummyContext()
    asyncio.run(admin_callback(update, context))
    assert data['pending'] == []
    assert 2 in data['products']['p1']['buyers']
    assert context.bot.sent[0][0] == 2


def test_start_admin_keyboard():
    update = DummyMessageUpdate(ADMIN_ID)
    context = DummyContext()
    asyncio.run(start(update, context))
    markup = update.replies[0][1]
    assert any(
        btn.text == tr('menu_admin', 'en') for row in markup.inline_keyboard for btn in row
    )


def test_admin_submenu_button():
    update = DummyCallbackUpdate(ADMIN_ID, 'menu:admin')
    context = DummyContext()
    asyncio.run(menu_callback(update, context))
    text, markup = update.replies[0]
    assert text == tr('menu_admin', 'en')
    buttons = [btn.text for row in markup.inline_keyboard for btn in row]
    assert tr('menu_pending', 'en') in buttons
    assert tr('menu_addproduct', 'en') in buttons
    assert tr('menu_editproduct', 'en') in buttons
    assert tr('menu_stats', 'en') in buttons


def test_adminmenu_addproduct_usage():
    update = DummyCallbackUpdate(ADMIN_ID, 'adminmenu:addproduct')
    context = DummyContext()
    asyncio.run(admin_menu_callback(update, context))

    msg_update = DummyMessageUpdate(ADMIN_ID)
    msg_context = DummyContext()
    asyncio.run(addproduct(msg_update, msg_context))
    text, _ = msg_update.replies[0]
    assert text == tr('ask_product_id', 'en')


def test_adminmenu_pending_list():
    data['pending'] = [{'user_id': 2, 'product_id': 'p1', 'file_id': 'f'}]
    update = DummyCallbackUpdate(ADMIN_ID, 'adminmenu:pending')
    context = DummyContext()
    asyncio.run(admin_menu_callback(update, context))
    text, markup = update.replies[0]
    assert tr('pending_entry', 'en').format(user_id=2, product_id='p1') == text
    assert markup.inline_keyboard[0][0].text == tr('approve_button', 'en')


def test_adminmenu_editproduct_buttons():
    data['products'] = {
        'p1': {'price': '1'},
        'p2': {'price': '2'},
    }
    update = DummyCallbackUpdate(ADMIN_ID, 'adminmenu:editproduct')
    context = DummyContext()
    asyncio.run(admin_menu_callback(update, context))
    text, markup = update.replies[0]
    assert text == tr('menu_editproduct', 'en')
    callbacks = [
        btn.callback_data
        for row in markup.inline_keyboard
        for btn in row
    ]
    assert 'editprod:p1' in callbacks
    assert 'editprod:p2' in callbacks
    assert markup.inline_keyboard[-1][0].callback_data == 'menu:admin'


def test_adminmenu_editproduct_no_products():
    data['products'] = {}
    update = DummyCallbackUpdate(ADMIN_ID, 'adminmenu:editproduct')
    context = DummyContext()
    asyncio.run(admin_menu_callback(update, context))
    text, _ = update.replies[0]
    assert text == tr('no_products', 'en')
