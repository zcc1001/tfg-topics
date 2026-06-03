from typing import Any

import pandas as pd
import streamlit as st


def render_best_params_summary(best_params_df: pd.DataFrame) -> None:
    st.subheader("Mejor configuración encontrada")
    st.caption(
        "Configuración del modelo que maximiza la coherencia "
        "según el proceso de optimización."
    )
    st.success(
        "Esta configuración se utiliza como resultado final"
        "del modelo para el análisis posterior."
    )
    row = best_params_df.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Modelo", row["model"])
    col2.metric("Best score (coherence)", f"{row['best_score']:.3f}")

    st.markdown("**Parámetros seleccionados:**")

    non_param_columns = {
        "model",
        "best_score",
        "num_topics",
        "run_id",
        "source",
    }

    params = {
        col: _format_param_value(row[col])
        for col in best_params_df.columns
        if col not in non_param_columns and not pd.isna(row[col])
    }

    st.json(params)


def _format_param_value(value: Any) -> float | int | str:
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, (int, str)):
        return value
    return str(value)
