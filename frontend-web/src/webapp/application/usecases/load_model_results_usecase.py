from webapp.application.ports.topic_model_repository import TopicModelRepository


class LoadModelResultsUseCase:
    """Use case to load topic model results from repository."""

    def __init__(self, repository: TopicModelRepository):
        self._repository = repository

    def execute(self, dataset: str, model_name: str) -> dict:
        """Load result from repository.

        Args:
            dataset (str): dataset file name without extension.
        """
        return {
            "model_summary": self._repository.load_model_info(
                dataset=dataset, model_name=model_name
            ),
            "topics": self._repository.load_topics(
                dataset=dataset, model_name=model_name
            ),
            "document_topics": self._repository.load_document_topics(
                dataset=dataset,
                model_name=model_name,
            ),
            "metrics": self._repository.load_metrics(
                dataset=dataset, model_name=model_name
            ),
            "params": self._repository.load_params(
                dataset=dataset, model_name=model_name
            ),
            "best_params": self._repository.load_best_hyperparams(
                dataset=dataset, model_name=model_name
            ),
            "trials": self._repository.load_hyperparams_trials(
                dataset=dataset, model_name=model_name
            ),
            "topic_coordinates": self._repository.load_topic_coordinates(
                dataset=dataset, model_name=model_name
            ),
        }
