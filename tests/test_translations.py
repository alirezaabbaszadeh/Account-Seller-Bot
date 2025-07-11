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
