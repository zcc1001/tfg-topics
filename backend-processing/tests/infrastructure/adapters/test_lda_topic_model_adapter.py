from __future__ import annotations

import sys
import types
from typing import Any

import numpy as np
import pytest

if "lda" not in sys.modules:
    mod_lda = types.ModuleType("lda")

    class _DummyLDA:
        def __init__(
            self,
            n_topics: Any = None,
            alpha: Any = None,
            n_iter: Any = None,
            eta: Any = None,
            random_state: Any = None,
        ) -> None:
            self.n_topics = n_topics
            self.alpha = alpha
            self.n_iter = n_iter
            self.eta = eta
            self.random_state = random_state
            # placeholders to be set by tests
            self.doc_topic_: Any = None
            self.topic_word_: Any = None

        def fit(self, doc_term_matrix: Any) -> None:
            # no-op in stub
            return None

    mod_lda.LDA = _DummyLDA  # type: ignore
    sys.modules["lda"] = mod_lda

import processing.infrastructure.adapters.modeling.lda_topic_model_adapter as mod
from processing.infrastructure.adapters.modeling.lda_topic_model_adapter import (
    LdaTopicModelAdapter,
)


class _FakeModel:
    def __init__(self, topic_word: np.ndarray, doc_topic: np.ndarray) -> None:
        self.topic_word_ = topic_word
        self.doc_topic_ = doc_topic


class _FakeStopwords:
    @staticmethod
    def words(_lang: str) -> set[str]:
        return set()


@pytest.fixture(autouse=True)
def _patch_nltk_stopwords(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "stopwords", _FakeStopwords)


def test_extract_topics_sorts_by_weight() -> None:
    """_extract_topics returns top feature names ordered by weight indices."""
    # Two topics, three features
    topic_word = np.array([[0.1, 0.9, 0.2], [0.5, 0.1, 0.4]])
    feature_names = ["f0", "f1", "f2"]

    topics = LdaTopicModelAdapter._extract_topics(topic_word, feature_names, top_n=2)

    assert topics[0] == ["f1", "f2"]
    assert topics[1] == ["f0", "f2"]


def test_extract_document_topics_builds_entries() -> None:
    """_extract_document_topics converts doc-topic matrix into list entries."""
    doc_topic = np.array([[0.2, 0.8], [0.6, 0.4]])

    results = LdaTopicModelAdapter._extract_document_topics(doc_topic)
    assert len(results) == 4
    assert any(r["document_id"] == 0 and r["topic_id"] == 1 for r in results)


def test_compute_coherence_uses_coherence_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_compute_coherence delegates to CoherenceModel and returns its score."""
    tokens = [["a", "b"], ["b", "c"]]
    topics = {0: ["a", "b"], 1: ["b", "c"]}

    class DummyCoherence:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def get_coherence(self) -> float:
            return 0.77

    monkeypatch.setattr(mod, "CoherenceModel", DummyCoherence)

    score = LdaTopicModelAdapter._compute_coherence(tokens, topics)
    assert pytest.approx(score, rel=1e-6) == 0.77


def test_preprocess_caches_and_removes_stopwords() -> None:
    """_preprocess tokenizes, removes stopwords and caches results."""
    adapter = LdaTopicModelAdapter(random_seed=0)
    docs = ["This is a test document.".lower(), "Another doc.".lower()]

    tokens1, joined1 = adapter._preprocess(docs)
    tokens2, joined2 = adapter._preprocess(docs)

    assert tokens1 is tokens2
    assert joined1 is joined2
    assert isinstance(tokens1, list)
    assert isinstance(joined1, list)


def test_compute_intertopic_coordinates_returns_coordinates() -> None:
    """
    _compute_intertopic_coordinates applies PCA to topic-word matrix
    and sums doc-topic sizes.
    """
    # Create simple topic_word: 2 topics x 3 features
    topic_word = np.array([[0.1, 0.9, 0.0], [0.4, 0.2, 0.4]])
    doc_topic = np.array([[0.2, 0.8], [0.5, 0.5]])

    class T(LdaTopicModelAdapter):
        def __init__(self) -> None:
            # avoid NLTK stopwords lookup
            self._cached_tokens = None
            self._cached_joined = None
            self.STOPWORDS = set()
            self.random_seed = 0

    t = T()
    coords = t._compute_intertopic_coordinates(topic_word, doc_topic)
    assert len(coords) == 2
    assert all(
        "topic_id" in c and "x" in c and "y" in c and "size" in c for c in coords
    )
