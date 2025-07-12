import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
from botlib.translations import tr  # noqa: E402


def test_tr_welcome_farsi():
    assert tr('welcome', 'fa').startswith('به بات')


def test_tr_product_not_found():
    assert tr('product_not_found', 'fa') == 'محصول یافت نشد'


def test_tr_default_english():
    assert tr('welcome', 'en') == 'Welcome! Use /products to list products.'


def test_tr_unauthorized():
    assert tr('unauthorized', 'en') == 'Unauthorized'
    assert tr('unauthorized', 'fa') == 'اجازه دسترسی ندارید'


def test_tr_menu_admin():
    assert tr('menu_admin', 'en') == 'Admin'
    assert tr('menu_admin', 'fa') == 'مدیریت'


def test_tr_menu_main():
    assert tr('menu_main', 'en') == 'Main menu'
    assert tr('menu_main', 'fa') == 'منوی اصلی'


def test_tr_back_button():
    assert tr('back_button', 'en') == 'Back'
    assert tr('back_button', 'fa') == 'بازگشت'
