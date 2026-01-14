import os
from pathlib import Path

import streamlit as st


def main() -> None:
    # in/out paths from environment variables
    project_root = Path(__file__).resolve().parents[3]
    default_data_dir = os.path.join(project_root, "data")
    data_dir = os.getenv("DATA_DIR", default_data_dir)
    processing_dir = os.path.join(data_dir, "processing")

    if "processing_dir" not in st.session_state:
        st.session_state["processing_dir"] = processing_dir

    st.set_page_config(page_title="TFG – Topic Modeling", layout="wide")

    analysis_page = st.Page(
        "ui/pages/model_analysis_page.py",
        title="Análisis por modelo",
        icon=":material/analytics:",
    )

    comparison_page = st.Page(
        "ui/pages/comparison_page.py",
        title="Comparativa de modelos",
        icon=":material/compare:",
    )

    pg = st.navigation([analysis_page, comparison_page])

    pg.run()


if __name__ == "__main__":
    main()
