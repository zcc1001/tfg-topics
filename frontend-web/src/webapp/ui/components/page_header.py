import streamlit as st


def render_page_header(page_title: str, description: str | None = None) -> None:
    st.header(page_title)
    if description:
        st.caption(description)
