from __future__ import annotations

import sys
import types
from typing import Any, Dict, List

import numpy as np
import pytest

if "bertopic" not in sys.modules:
    mod_bertopic = types.ModuleType("bertopic")

    class _DummyBERTopic:
        pass

    setattr(mod_bertopic, "BERTopic", _DummyBERTopic)
    sys.modules["bertopic"] = mod_bertopic

if "sentence_transformers" not in sys.modules:
    mod_sent = types.ModuleType("sentence_transformers")

    def _dummy_sentence_transformer(*args: Any, **kwargs: Any) -> None:
        return None

    setattr(mod_sent, "SentenceTransformer", _dummy_sentence_transformer)
    sys.modules["sentence_transformers"] = mod_sent

import processing.infrastructure.adapters.modeling.bertopic_model_adapter as mod
from processing.infrastructure.adapters.modeling.bertopic_model_adapter import (
    BerTopicModelAdapter,
)


class _FakeModel:
    def __init__(
        self, topic_sizes: dict, topics_map: dict, embeddings: Any = None
    ) -> None:
        self.topic_sizes_ = topic_sizes
        self._topics_map = topics_map
        self.topic_embeddings_ = embeddings

    def get_topic(self, topic_id: int) -> Any:
        return self._topics_map.get(topic_id)


class _FakeStopwords:
    @staticmethod
    def words(_lang: str) -> set[str]:
        return set()


@pytest.fixture(autouse=True)
def _patch_nltk_stopwords(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "stopwords", _FakeStopwords)


def test_extract_topics_filters_and_formats() -> None:
    """_extract_topics returns only valid topic words and skips invalid entries."""
    # topic_sizes includes an int key and an invalid (non-Integral) key
    topic_sizes = {0: 10, "bad": 1, -1: 1, 1: 5}
    topics_map = {
        0: [("w1", 0.5), ("w2", 0.3), ("bad", "x")],
        1: "not-a-list",
    }

    model = _FakeModel(topic_sizes=topic_sizes, topics_map=topics_map)

    # Use a subclass to exercise protected behaviour from a subclass context
    class T(BerTopicModelAdapter):
        pass

    topics = T._extract_topics(model, top_n=2)  # type: ignore

    assert 0 in topics
    assert topics[0] == ["w1", "w2"]
    assert 1 not in topics


def test_extract_document_topics_skips_negative_topic_ids() -> None:
    """
    _extract_document_topics produces entries for non -1 topics
    with probabilities.
    """
    doc_topics = [0, -1, 1]
    probs = np.array([[0.7, 0.3], [0.0, 0.0], [0.2, 0.8]])

    class T(BerTopicModelAdapter):
        pass

    results = T._extract_document_topics(doc_topics, probs)  # type: ignore

    # Document 1 had topic -1 and should be skipped. Documents 0 and 2 produce
    # entries for each topic id in the probs array.
    assert any(r["document_id"] == 0 for r in results)
    assert all(r["document_id"] != 1 for r in results)
    assert any(r["document_id"] == 2 for r in results)


def test_compute_coherence_penalty_and_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    _compute_coherence returns -1.0 when no topics and delegates to
    CoherenceModel otherwise.
    """
    tokens = [["a", "b"], ["b", "c"]]

    # Empty topics -> penalized
    class T(BerTopicModelAdapter):
        pass

    score = T._compute_coherence(tokens, {})
    assert score == -1.0

    # Prepare topics with words that exist in the dictionary
    topics = {0: ["a", "b"], 1: ["b", "c"]}

    class DummyCoherence:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def get_coherence(self) -> float:
            return 0.42

    monkeypatch.setattr(mod, "CoherenceModel", DummyCoherence)

    score2 = T._compute_coherence(tokens, topics)
    assert pytest.approx(score2, rel=1e-6) == 0.42


def test_preprocess_caches_and_filters() -> None:
    """_preprocess removes stopwords and caches the tokenization result."""

    class T(BerTopicModelAdapter):
        pass

    adapter = T(random_seed=0)

    docs = ["This is a test of filtering stopwords".lower()]
    tokens1 = adapter._preprocess(docs)
    tokens2 = adapter._preprocess(docs)

    # cached result should be returned and identical
    assert tokens1 is tokens2
    assert all(isinstance(t, list) for t in tokens1)


def test_compute_intertopic_coordinates_various_cases() -> None:
    """
    _compute_intertopic_coordinates returns empty for invalid embeddings
    and computes coordinates for valid ones.
    """
    # Invalid embeddings (not ndarray)
    model_bad = _FakeModel(topic_sizes={0: 1}, topics_map={}, embeddings=None)

    class T(BerTopicModelAdapter):
        def compute_intertopic_coordinates(self, model: Any) -> List[Dict[str, Any]]:
            return self._compute_intertopic_coordinates(model)  # type: ignore

    t = T(random_seed=0)

    assert t.compute_intertopic_coordinates(model_bad) == []

    # Too small embeddings (ndim mismatch)
    model_small = _FakeModel(
        topic_sizes={0: 1}, topics_map={}, embeddings=np.array([1, 2, 3])
    )
    assert t.compute_intertopic_coordinates(model_small) == []

    # Valid embeddings: 3 topics x 3 features
    embeddings = np.array([[0.1, 0.2, 0.3], [0.0, 0.5, -0.1], [0.2, -0.2, 0.4]])
    topic_sizes = {0: 10, 1: 5, 2: 2}
    model_ok = _FakeModel(topic_sizes=topic_sizes, topics_map={}, embeddings=embeddings)

    coords = t.compute_intertopic_coordinates(model_ok)
    assert len(coords) == 3
    assert all(
        "topic_id" in c and "x" in c and "y" in c and "size" in c for c in coords
    )
