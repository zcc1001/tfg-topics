import pandas as pd
import plotly.express as px
import streamlit as st


def render_trial_score_evolution(trials_df: pd.DataFrame) -> None:
    st.subheader("Evolución de la búsqueda de hiperparámetros")
    st.caption(
        "Evolución del valor de coherencia a lo largo de "
        "las distintas pruebas realizadas durante la optimización."
    )
    # Identificar mejor trial
    best_row = trials_df.loc[trials_df["score"].idxmax()]
    best_trial_id = best_row["trial_id"]
    best_score = best_row["score"]

    # Scatter + línea
    fig = px.scatter(
        trials_df,
        x="trial_id",
        y="score",
        labels={
            "trial_id": "Trial",
            "score": "Coherence",
        },
    )

    # Marcar mejor trial
    fig.add_scatter(
        x=[best_trial_id],
        y=[best_score],
        mode="markers+text",
        marker=dict(
            size=14,
            color="crimson",
            symbol="star",
        ),
        text=[f"Best (trial {best_trial_id})"],
        textposition="top center",
        showlegend=False,
    )

    fig.update_layout(
        title="Score (coherence) por trial",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#E6E6E6"),
        yaxis=dict(showgrid=True, gridcolor="#E6E6E6"),
        margin=dict(l=40, r=40, t=40, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)
