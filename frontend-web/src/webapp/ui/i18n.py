import json
import logging
from pathlib import Path
from typing import Any, cast

import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_data
def _load_translations(lang: str) -> dict[str, Any]:
    """Loads and caches the translation dictionary
    for a specific language. (cache bust)"""
    base_dir = Path(__file__).resolve().parent.parent
    locale_path = base_dir / "locales" / f"{lang}.json"

    if not locale_path.exists():
        logger.warning(f"Translation file not found: {locale_path}, falling back to es")
        fallback_path = base_dir / "locales" / "es.json"
        if not fallback_path.exists():
            return {}
        with open(fallback_path, "r", encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))

    with open(locale_path, "r", encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def _(key: str) -> str:
    """
    Translates a key based on the current session_state language.
    Supports nested keys like "menu.profile_selector".
    """
    lang = st.session_state.get("lang", "es")
    translations = _load_translations(lang)

    keys = key.split(".")
    current = translations
    try:
        for k in keys:
            current = current[k]
        return str(current)
    except (KeyError, TypeError):
        logger.debug(f"Missing translation for key: {key} in lang: {lang}")
        return key


def language_selector() -> None:
    """Renders a language selector in the sidebar."""
    options = {"es": "🇪🇸 ES", "en": "🇬🇧 EN"}

    current_lang = st.session_state.get("lang", "es")

    def on_change() -> None:
        st.session_state["lang"] = st.session_state["_lang_selector"]

    st.sidebar.selectbox(
        _("menu.language_selector"),
        options=list(options.keys()),
        format_func=lambda x: options[x],
        index=list(options.keys()).index(current_lang),
        key="_lang_selector",
        on_change=on_change,
    )
