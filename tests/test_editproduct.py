import sys
from pathlib import Path
import types
import asyncio
import os

os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("ADMIN_PHONE", "+111")
os.environ.setdefault("FERNET_KEY", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import editproduct, data, ADMIN_ID  # noqa: E402


class DummyUpdate:
    def __init__(self, user_id):
        self.message = types.SimpleNamespace(
            from_user=types.SimpleNamespace(id=user_id),
            reply_text=self._reply,
        )
        self.effective_user = self.message.from_user
        self.replies = []

    async def _reply(self, text):
        self.replies.append(text)


class DummyContext:
    def __init__(self, args):
        self.args = args
        self.user_data = {}


def test_editproduct_updates_name():
    data['products'] = {
        'p1': {'price': '1', 'username': 'u', 'password': 'p', 'secret': 's'}
    }
    update = DummyUpdate(ADMIN_ID)
    context = DummyContext(['p1', 'name', 'New', 'Name'])
    asyncio.run(editproduct(update, context))
    assert data['products']['p1']['name'] == 'New Name'
