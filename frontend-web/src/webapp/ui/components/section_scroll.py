import streamlit as st
import streamlit.components.v1 as components


def render_section_anchor(anchor_id: str) -> None:
    st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)


def scroll_to_section(anchor_id: str | None) -> None:
    if anchor_id is None:
        return

    components.html(
        f"""
        <script>
        const scrollToAnchor = () => {{
            const target = window.parent.document.getElementById("{anchor_id}");
            if (target) {{
                target.scrollIntoView({{ behavior: "smooth", block: "start" }});
            }}
        }};
        window.setTimeout(scrollToAnchor, 120);
        </script>
        """,
        height=0,
    )
