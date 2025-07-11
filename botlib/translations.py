TRANSLATIONS = {
    'hello': {
        'en': 'Hello',
        'fa': 'سلام',
    },
    'bye': {
        'en': 'Goodbye',
        'fa': 'خداحافظ',
    },
}


def tr(key: str, lang: str = 'en') -> str:
    """Return the translation for *key* in the given language."""
    return TRANSLATIONS.get(key, {}).get(lang, key)
