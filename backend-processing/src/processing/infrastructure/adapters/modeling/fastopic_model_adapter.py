import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastopic import FASTopic
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from processing.application.ports.topic_model_port import TopicModelPort
from processing.application.services.domain_stopwords import (
    DOMAIN_STOPWORDS,
    LATEX_STOPWORDS,
)
from processing.application.services.latex_text_processor import LatexTextProcessor
from processing.domain.entities import TopicModelResult

logger = logging.getLogger(__name__)


class FastTopicModelAdapter(TopicModelPort):

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
        return "fastopic"

    def suggest_params(self, trial: Any) -> Dict[str, Any]:
        return {
            "num_topics": trial.suggest_int("num_topics", 2, 30),
            "num_top_words": trial.suggest_int("num_top_words", 5, 15),
            "epochs": trial.suggest_int("epochs", 100, 300),
            "learning_rate": trial.suggest_float("learning_rate", 1e-4, 5e-3),
        }

    def _train(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> Tuple[FASTopic, List[str], np.ndarray]:

        model = FASTopic(
            num_topics=params["num_topics"],
            num_top_words=params["num_top_words"],
            doc_embed_model="all-MiniLM-L6-v2",
            verbose=False,
        )

        top_words, theta = model.fit_transform(
            texts,
            epochs=params["epochs"],
            learning_rate=params["learning_rate"],
        )

        logger.info("FASTTopic training completed.")
        return model, top_words, theta

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
        return coherence

    def fit(
        self,
        dataset: str,
        texts: List[str],
        params: Dict[str, Any],
        dataset_hash: str,
    ) -> TopicModelResult:
        start_time = time.perf_counter()
        clean_texts = [LatexTextProcessor.clean(doc) for doc in texts]
        tokens = self._preprocess(clean_texts)

        model, _, theta = self._train(clean_texts, params)

        topics = self._extract_topics(model)
        document_topics = self._extract_document_topics(theta)

        coherence = self._compute_coherence(tokens, topics)
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
            dataset_hash=dataset_hash,
        )

    @staticmethod
    def _extract_topics(
        model: FASTopic,
    ) -> Dict[int, List[str]]:

        topics: Dict[int, List[str]] = {}

        for topic_id, topic_str in enumerate(model.top_words):
            words = topic_str.split()
            if len(words) >= 2:
                topics[topic_id] = words

        return topics

    @staticmethod
    def _extract_document_topics(
        theta: np.ndarray,
    ) -> List[Dict[str, Any]]:

        results: List[Dict[str, Any]] = []
        for doc_id in range(theta.shape[0]):
            for topic_id, prob in enumerate(theta[doc_id]):
                results.append(
                    {
                        "document_id": doc_id,
                        "topic_id": topic_id,
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
            return -1.0

        dictionary = Dictionary(tokens)

        filtered_topics = []
        for words in topics.values():
            valid = [w for w in words if w in dictionary.token2id]
            if len(valid) >= 2:
                filtered_topics.append(valid)

        if not filtered_topics:
            return -1.0

        model = CoherenceModel(
            topics=filtered_topics,
            texts=tokens,
            dictionary=dictionary,
            coherence="c_v",
        )

        return float(model.get_coherence())

    def _preprocess(
        self,
        documents: List[str],
    ) -> List[List[str]]:

        if self._cached_tokens is not None:
            return self._cached_tokens

        tokens = [
            [t for t in simple_preprocess(doc) if t not in self.STOPWORDS]
            for doc in documents
        ]
        self._cached_tokens = tokens
        return tokens

    @staticmethod
    def _compute_intertopic_coordinates(
        model: FASTopic,
    ) -> List[Dict[str, Any]]:

        embeddings = model.topic_embeddings
        if embeddings.shape[0] < 2:
            return []

        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(embeddings)

        return [
            {
                "topic_id": int(i),
                "x": float(x),
                "y": float(y),
                "size": 1.0,
            }
            for i, (x, y) in enumerate(coords)
        ]
