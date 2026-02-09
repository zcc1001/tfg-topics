from processing.application.ports.dataset_state_port import DatasetStatePort


class EnsureProcessingDatasetConsistencyUseCase:
    """
    Ensures that model processing results are consistent with the current dataset.
    """

    def __init__(self, dataset_state_port: DatasetStatePort):
        self._state = dataset_state_port

    def execute(self, dataset: str, model_name: str) -> str:
        """
        Returns the dataset_hash that MUST be used for this processing run.
        """

        current_hash = self._state.read_dataset_hash()
        if current_hash is None:
            raise RuntimeError(
                "Dataset hash not found. Ingestion must be executed first."
            )

        self._state.invalidate_mismatched_results(
            dataset=dataset,
            current_hash=current_hash,
        )

        return current_hash
