import pandas as pd
import plotly.express as px
import streamlit as st


def render_intertopic_distance_map(coords_df: pd.DataFrame) -> None:
    df = coords_df.copy()
    st.subheader("Mapa de distancia entre tópicos")
    st.caption(
        "Proyección bidimensional de los tópicos en el espacio latente. "
        "La distancia entre círculos refleja su separación semántica."
    )
    st.caption(
        "Los tamaños de los círculos indican la relevancia relativa de cada tópico."
    )
    # 1. Normalizar tamaño de burbujas
    df["size_norm"] = df["size"] / df["size"].max() * 80
    df["topic_id_str"] = df["topic_id"].astype(str)

    # 2. Scatter principal (color por tópico)
    fig = px.scatter(
        df,
        x="x",
        y="y",
        size="size_norm",
        color="topic_id_str",  # <-- CLAVE
        text="topic_id",
        title="Intertopic Distance Map",
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data={
            "topic_id": True,
            "size": True,
            "x": False,
            "y": False,
            "size_norm": False,
        },
    )

    # 3. Estilo de burbujas y texto
    fig.update_traces(
        marker=dict(
            opacity=0.75,
            line=dict(
                width=1.5,
                color="#5A5A5A",
            ),
        ),
        textposition="middle center",
        textfont=dict(
            size=13,
            color="#2F2F2F",
        ),
    )

    # 4. Layout general
    fig.update_layout(
        showlegend=True,  # ahora sí tiene sentido
        legend_title_text="Tópico",
        plot_bgcolor="white",
        paper_bgcolor="white",
        title=dict(x=0.02, xanchor="left", font=dict(size=20)),
        xaxis=dict(
            title="D1",
            showgrid=True,
            gridcolor="#E6E6E6",
            zeroline=False,
        ),
        yaxis=dict(
            title="D2",
            showgrid=True,
            gridcolor="#E6E6E6",
            zeroline=False,
        ),
        shapes=[
            dict(
                type="line",
                x0=0,
                x1=0,
                y0=df["y"].min(),
                y1=df["y"].max(),
                line=dict(color="#CFCFCF", width=1),
            ),
            dict(
                type="line",
                x0=df["x"].min(),
                x1=df["x"].max(),
                y0=0,
                y1=0,
                line=dict(color="#CFCFCF", width=1),
            ),
        ],
        margin=dict(l=40, r=40, t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)
