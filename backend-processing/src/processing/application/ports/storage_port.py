from abc import ABC, abstractmethod

from processing.domain.entities import HyperparameterSearchResult, TopicModelResult


class StoragePort(ABC):
    """Interface for persisting topic modeling results and metadata.

    This port defines the contract for storage adapters that handle writing
    data generated during the topic modeling process, such as hyperparameter
    optimization outcomes and the final model results.
    """

    @abstractmethod
    def write_hyperparameter_search(
        self,
        result: HyperparameterSearchResult,
    ) -> None:
        """Writes the results of a hyperparameter search to storage.

        Args:
            result (HyperparameterSearchResult): The object containing the search
                results, including trials and best parameters.

        Raises:
            NotImplementedError: This is an abstract method and must be
                implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def write_topic_model_result(
        self,
        run_id: str,
        result: TopicModelResult,
    ) -> None:
        """Writes the results of a topic model run to storage.

        Args:
            run_id (str): A unique identifier for the modeling run.
            result (TopicModelResult): The object containing the trained model's
                output, such as topics, document mappings, and metrics.

        Raises:
            NotImplementedError: This is an abstract method and must be
                implemented by subclasses.
        """
        raise NotImplementedError
