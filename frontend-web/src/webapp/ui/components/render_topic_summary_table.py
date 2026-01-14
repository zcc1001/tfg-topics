import pandas as pd
import streamlit as st


def render_topic_summary_table(topics_df: pd.DataFrame, max_words: int = 10) -> None:

    df = topics_df.sort_values(["topic_id", "rank"])

    df = df[df["rank"] <= max_words]

    summary_df = (
        df.groupby("topic_id")["word"]
        .apply(lambda words: " , ".join(words))
        .reset_index(name="top_words")
    )

    st.subheader("Resumen de tópicos")
    st.caption(
        "Resumen textual de cada tópico mediante sus palabras clave más relevantes, "
        "ordenadas por peso."
    )
    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )
