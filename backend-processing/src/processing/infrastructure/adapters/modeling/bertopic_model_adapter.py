import logging
import time
from numbers import Integral, Real
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from bertopic import BERTopic
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.domain_stopwords import (
    DOMAIN_STOPWORDS,
    LATEX_STOPWORDS,
)
from processing.application.services.latex_text_processor import LatexTextProcessor
from processing.domain.entities import TopicModelResult

logger = logging.getLogger(__name__)


class BerTopicModelAdapter(TopicModelPort):

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

        SPANISH_STOPWORDS = set(stopwords.words("spanish"))
        self.STOPWORDS = (
            ENGLISH_STOP_WORDS.union(SPANISH_STOPWORDS)
            .union(LATEX_STOPWORDS)
            .union(DOMAIN_STOPWORDS)
        )

        self._cached_tokens: Optional[List[List[str]]] = None

    def model_name(self) -> str:
        return "bertopic"

    def suggest_params(self, trial: Any) -> Dict[str, Any]:
        return {
            "min_topic_size": trial.suggest_int("min_topic_size", 1, 10),
            "n_neighbors": trial.suggest_int("n_neighbors", 2, 15),
            "n_components": trial.suggest_int("n_components", 2, 50),
            "ngram_min": trial.suggest_int("ngram_min", 1, 1),
            "ngram_max": trial.suggest_int("ngram_max", 1, 2),
        }

    def _train(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> Tuple[BERTopic, List[int], Optional[np.ndarray]]:

        vectorizer = CountVectorizer(
            stop_words=list(self.STOPWORDS),
            ngram_range=(params["ngram_min"], params["ngram_max"]),
        )

        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        model = BERTopic(
            embedding_model=embedding_model,
            vectorizer_model=vectorizer,
            min_topic_size=params["min_topic_size"],
            calculate_probabilities=True,
            verbose=False,
        )

        topics, probs = model.fit_transform(texts)
        logger.info("BERTopic model training completed.")

        return model, topics, probs

    def train_and_evaluate(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> float:
        clean_texts = [LatexTextProcessor.clean(doc) for doc in texts]
        tokens = self._preprocess(clean_texts)

        model, _, _ = self._train(clean_texts, params)
        topics = self._extract_topics(model)

        coherence = self._compute_coherence(tokens, topics)
        logger.info("Evaluation finished. Coherence score: %.4f", coherence)

        return coherence

    def fit(
        self,
        dataset: str,
        texts: List[str],
        params: Dict[str, Any],
    ) -> TopicModelResult:

        logger.info("Fitting BERTopic model to %d documents.", len(texts))
        start_time = time.perf_counter()

        clean_texts = [LatexTextProcessor.clean(doc) for doc in texts]
        tokens = self._preprocess(clean_texts)

        model, doc_topics, probs = self._train(clean_texts, params)

        topics = self._extract_topics(model)

        # --- NORMALIZE probs ---
        if probs is None:
            logger.warning(
                "BERTopic returned probs=None; falling back to one-hot encoding."
            )
            num_topics = len(topics)
            probs = np.zeros((len(doc_topics), num_topics))

            for i, topic_id in enumerate(doc_topics):
                if topic_id != -1 and topic_id < num_topics:
                    probs[i, topic_id] = 1.0

        document_topics = self._extract_document_topics(doc_topics, probs)

        coherence = self._compute_coherence(tokens, topics)
        logger.info("Computed coherence score: %.4f", coherence)

        topic_coordinates = self._compute_intertopic_coordinates(model)

        end_time = time.perf_counter()
        runtime_seconds = end_time - start_time

        return TopicModelResult(
            dataset=dataset,
            model_name=self.model_name(),
            topics=topics,
            document_topics=document_topics,
            metrics={"coherence": coherence},
            params=params,
            topic_coordinates=topic_coordinates,
            runtime_seconds=runtime_seconds,
        )

    @staticmethod
    def _extract_topics(
        model: BERTopic,
        top_n: int = 10,
    ) -> Dict[int, List[str]]:

        topics: Dict[int, List[str]] = {}

        topic_sizes = model.topic_sizes_
        if topic_sizes is None:
            return topics

        for raw_topic_id in topic_sizes.keys():
            if not isinstance(raw_topic_id, Integral):
                continue

            topic_id = int(raw_topic_id)
            if topic_id == -1:
                continue

            topic_words_raw = model.get_topic(topic_id)

            if not isinstance(topic_words_raw, list):
                continue

            valid_words: list[tuple[str, float]] = []
            for item in topic_words_raw:
                if (
                    isinstance(item, tuple)
                    and len(item) == 2
                    and isinstance(item[0], str)
                    and isinstance(item[1], Real)
                ):
                    valid_words.append((item[0], float(item[1])))

            if not valid_words:
                continue

            topics[topic_id] = [word for word, _ in valid_words[:top_n]]

        return topics

    @staticmethod
    def _extract_document_topics(
        doc_topics: List[int],
        probs: np.ndarray,
    ) -> List[Dict[str, Any]]:

        results = []
        for doc_id, topic_id in enumerate(doc_topics):
            if topic_id == -1:
                continue

            for t_id, prob in enumerate(probs[doc_id]):
                results.append(
                    {
                        "document_id": doc_id,
                        "topic_id": t_id,
                        "probability": float(prob),
                    }
                )

        return results

    @staticmethod
    def _compute_coherence(
        tokens: List[List[str]],
        topics: Dict[int, List[str]],
    ) -> float:

        if not topics:
            logger.warning(
                "No valid topics found. Returning penalized coherence score."
            )
            return -1.0
        dictionary = Dictionary(tokens)

        filtered_topics: list[list[str]] = []
        for words in topics.values():
            if not isinstance(words, list):
                continue

            valid_words = [
                w for w in words if isinstance(w, str) and w in dictionary.token2id
            ]

            if len(valid_words) >= 2:
                filtered_topics.append(valid_words)

        if not filtered_topics:
            return -1.0
        coherence_model = CoherenceModel(
            topics=filtered_topics,
            texts=tokens,
            dictionary=dictionary,
            coherence="c_v",
        )

        return float(coherence_model.get_coherence())

    def _preprocess(
        self,
        documents: List[str],
    ) -> List[List[str]]:

        if self._cached_tokens is not None:
            return self._cached_tokens

        tokens = [
            [token for token in simple_preprocess(doc) if token not in self.STOPWORDS]
            for doc in documents
        ]

        self._cached_tokens = tokens
        return tokens

    @staticmethod
    def _compute_intertopic_coordinates(
        model: BERTopic,
    ) -> List[Dict[str, Any]]:

        result: List[Dict[str, Any]] = []

        embeddings = model.topic_embeddings_
        topic_sizes = model.topic_sizes_

        # Defensive checks for static typing and runtime safety
        if not isinstance(embeddings, np.ndarray):
            return result

        if embeddings.ndim != 2:
            return result

        n_topics, n_features = embeddings.shape

        # --- CRITICAL CHECK ---
        if n_topics < 2 or n_features < 2:
            # Not enough data to compute 2D projection
            return result

        if topic_sizes is None:
            return result

        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(embeddings)

        for idx, (x, y) in enumerate(coords):
            size = topic_sizes.get(idx, 0)
            result.append(
                {
                    "topic_id": int(idx),
                    "x": float(x),
                    "y": float(y),
                    "size": float(size),
                }
            )

        return result
