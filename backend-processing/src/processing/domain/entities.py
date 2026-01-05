from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Document:
    text: str
    source: str
    metadata: Dict[str, Any] | None = None


@dataclass
class TopicModelResult:
    source: str
    model_name: str
    topics: Dict[int, List[str]]
    document_topics: List[Dict[str, Any]]
    metrics: Dict[str, float]
    params: Dict[str, Any]
    topic_coordinates: list


@dataclass
class HyperparameterTrialResult:
    trial_id: int
    model_name: str
    params: Dict[str, Any]
    score: float
    state: str


@dataclass
class HyperparameterSearchResult:
    model_name: str
    source: str
    best_params: Dict[str, Any]
    best_score: float
    trials: List[HyperparameterTrialResult]
