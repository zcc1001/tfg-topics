from abc import ABC, abstractmethod
from typing import Any, Dict, List

from processing.domain.entities import TopicModelResult


class TopicModelPort(ABC):
    """Create a topic model model ."""

    @abstractmethod
    def fit(self, dataset: str, texts: List[str], params: Dict) -> TopicModelResult:
        """Fit the model to the given texts.

        Args:
            dataset (str): Identifier for the data source (e.g., 'issues', 'thesis').
            texts (List[str]): A list of documents to train the model on.
            params (Dict): Hyperparameters for the topic model.

        Raises:
            NotImplementedError: This is an abstract method and must be implemented
            by subclasses.

        Returns:
            TopicModelResult: An object containing the results of the topic modeling.
        """
        raise NotImplementedError

    @abstractmethod
    def suggest_params(self, trial: Any) -> Dict[str, Any]:
        """Suggest a set of hyperparameters for an optimization trial.

        Args:
            trial: An optimization trial object (e.g., from Optuna).

        Raises:
            NotImplementedError: This is an abstract method and must be
                implemented by subclasses.

        Returns:
            A dictionary of suggested hyperparameters for the model.
        """
        raise NotImplementedError

    @abstractmethod
    def train_and_evaluate(
        self,
        texts: List[str],
        params: Dict[str, Any],
    ) -> float:
        """Train the model with given parameters and evaluate its performance.

        This method is typically used during hyperparameter optimization.

        Args:
            texts (List[str]): The list of documents to train on.
            params (Dict[str, Any]): The dictionary of hyperparameters to use
            for training.

        Raises:
            NotImplementedError: This is an abstract method and must be
                implemented by subclasses.

        Returns:
            float: An evaluation score (e.g., coherence) for the trained model.
        """
        raise NotImplementedError

    @abstractmethod
    def model_name(self) -> str:
        """Get the name of the topic model.

        Raises:
            NotImplementedError: This is an abstract method and must be
                implemented by subclasses.

        Returns:
            str: The model's name as a string (e.g., 'lda', 'bertopic').
        """
        raise NotImplementedError
