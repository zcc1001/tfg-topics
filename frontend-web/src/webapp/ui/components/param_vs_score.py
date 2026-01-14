import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


def render_param_vs_score(trials_df: pd.DataFrame) -> None:
    st.subheader("Influencia de los hiperparámetros")
    st.caption(
        "Relación entre el valor de un hiperparámetro concreto "
        "y la coherencia obtenida en cada prueba."
    )
    numeric_params = _get_numeric_hyperparams(trials_df)

    if not numeric_params:
        st.info("No hay hiperparámetros numéricos para visualizar.")
        return

    param = st.selectbox(
        "Selecciona hiperparámetro",
        numeric_params,
    )

    df = trials_df.copy()

    if pd.api.types.is_integer_dtype(df[param]):
        df[f"{param}_jitter"] = df[param] + np.random.uniform(-0.05, 0.05, size=len(df))
        x_col = f"{param}_jitter"
    else:
        x_col = param

    best_row = df.loc[df["score"].idxmax()]

    fig = px.scatter(
        df,
        x=x_col,
        y="score",
        labels={
            x_col: param,
            "score": "Coherence",
        },
    )

    fig.add_scatter(
        x=df[x_col],
        y=df["score"],
        mode="lines",
        line=dict(color="lightgray", dash="dot"),
        showlegend=False,
    )

    fig.add_scatter(
        x=[best_row[x_col]],
        y=[best_row["score"]],
        mode="markers+text",
        marker=dict(size=14, color="crimson", symbol="star"),
        text=["Max coherence"],
        textposition="top center",
        showlegend=False,
    )

    fig.update_layout(
        title=f"Score vs {param}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#E6E6E6"),
        yaxis=dict(showgrid=True, gridcolor="#E6E6E6"),
        margin=dict(l=40, r=40, t=40, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def _get_numeric_hyperparams(trials_df: pd.DataFrame) -> list[str]:
    excluded_cols = {
        "model",
        "score",
        "run_id",
        "trial",
        "source",
    }

    numeric_cols = [
        col
        for col in trials_df.columns
        if col not in excluded_cols
        and pd.api.types.is_numeric_dtype(trials_df[col])
        and trials_df[col].notna().any()
    ]

    return numeric_cols
