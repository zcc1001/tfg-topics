import pandas as pd
import plotly.express as px
import streamlit as st


def render_doc_topic_distribution(doc_topics_df: pd.DataFrame) -> None:
    df = doc_topics_df.copy()

    doc_ids = sorted(df["document_id"].unique().tolist())
    doc_options = ["Todos"] + doc_ids

    st.subheader("Distribución documento–tópico")
    st.caption(
        "Distribución de la probabilidad de asignación de cada documento  "
        "a los distintos temas del modelo."
    )
    st.caption(
        "Cada punto representa la probabilidad de que un documento"
        " pertenezca a un tema concreto."
    )
    selected_doc = st.selectbox(
        "Selecciona documento",
        doc_options,
    )

    if selected_doc != "Todos":
        df = df[df["document_id"] == selected_doc]

    df = df[df["probability"] > 0.05]

    df["topic_id_str"] = df["topic_id"].astype(str)
    df["size_norm"] = (df["probability"] ** 0.5) * 40

    fig = px.scatter(
        df,
        x="document_id",
        y="topic_id_str",
        size="size_norm",
        color="topic_id_str",
        title="Distribución documento–tópico",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data={
            "document_id": True,
            "topic_id": True,
            "probability": True,
        },
    )

    fig.update_traces(
        marker=dict(
            opacity=0.8,
            line=dict(width=0.5, color="#555"),
        )
    )

    fig.update_layout(
        showlegend=True,
        legend_title_text="Tópico",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title="Documento",
            showgrid=True,
            gridcolor="#E6E6E6",
        ),
        yaxis=dict(
            title="Tópico",
            type="category",
        ),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)
