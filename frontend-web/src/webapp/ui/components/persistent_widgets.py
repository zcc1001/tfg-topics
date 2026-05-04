from collections.abc import Sequence
from typing import TypeVar, cast

import streamlit as st

T = TypeVar("T")


def persistent_selectbox(
    label: str,
    options: Sequence[T],
    state_key: str,
    widget_key: str,
    index: int = 0,
    placeholder: str | None = None,
) -> T:
    if not options:
        raise ValueError("Selectbox options cannot be empty.")

    default_value = options[index] if 0 <= index < len(options) else options[0]
    if st.session_state.get(state_key) not in options:
        st.session_state[state_key] = default_value

    st.session_state[widget_key] = st.session_state[state_key]

    def _sync_value() -> None:
        st.session_state[state_key] = st.session_state[widget_key]

    return cast(
        T,
        st.selectbox(
            label,
            options,
            key=widget_key,
            on_change=_sync_value,
            placeholder=placeholder,
        ),
    )


def persistent_multiselect(
    label: str,
    options: Sequence[T],
    state_key: str,
    widget_key: str,
) -> list[T]:
    selected_values = st.session_state.get(state_key, list(options))
    selected_values = [value for value in selected_values if value in options]
    if not selected_values:
        selected_values = list(options)

    st.session_state[state_key] = selected_values
    st.session_state[widget_key] = selected_values

    def _sync_values() -> None:
        st.session_state[state_key] = st.session_state[widget_key]

    return cast(
        list[T],
        st.multiselect(
            label,
            options,
            key=widget_key,
            on_change=_sync_values,
        ),
    )
