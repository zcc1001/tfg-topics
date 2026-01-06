import logging
from typing import List

import optuna

from processing.application.ports.topic_model_port import TopicModelPort
from processing.domain.entities import (
    HyperparameterSearchResult,
    HyperparameterTrialResult,
)

logger = logging.getLogger(__name__)


class HyperparameterSearchService:
    """Performs hyperparameter search for a topic model."""

    def __init__(
        self, n_trials: int = 20, random_seed: int = 42, timeout: int | None = None
    ):
        """Initializes the hyperparameter search service.
        Args:
            n_trials: The number of trials to run.
            random_seed: The random seed for reproducibility.
            timeout: The timeout for the search in seconds.
        """
        self.n_trials = n_trials
        self.random_seed = random_seed
        self.timeout = timeout

    def search(
        self, dataset: str, model_wrapper: TopicModelPort, texts: List[str]
    ) -> HyperparameterSearchResult:
        """Performs a hyperparameter search on the given texts.
        Args:
            dataset: The name of the data source.
            model_wrapper: The topic model wrapper to use for the search.
            texts: The texts to use for the search.
        Raises:
            RuntimeError: If the search fails with no successful trials.
        Returns:
            The results of the hyperparameter search.
        """
        logger.info(
            "Starting hyperparameter search ( %s trials, %s timeout )",
            self.n_trials,
            self.timeout,
        )

        # Guard against empty input texts
        if not texts:
            logger.warning("No documents to train on after cleaning.")
            raise RuntimeError("No documents to train on after cleaning.")

        # init optuna
        sampler = optuna.samplers.TPESampler(seed=self.random_seed)
        study = optuna.create_study(direction="maximize", sampler=sampler)

        def objective(trial: optuna.Trial) -> float:
            params = model_wrapper.suggest_params(trial)
            logger.debug("Trial %s - params: %s", trial.number, params)

            try:
                score = model_wrapper.train_and_evaluate(texts=texts, params=params)
            except Exception as exc:
                logger.warning("Trial %s failed.", trial.number, exc_info=True)
                logger.error(exc)
                raise optuna.TrialPruned()

            logger.debug("Trial %s - score: %s", trial.number, score)
            return score

        study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True,
        )
        if len(study.trials) == 0 or all(
            t.state != optuna.trial.TrialState.COMPLETE for t in study.trials
        ):
            raise RuntimeError("Hyperparameter search failed: no successful trials.")

        logger.info(
            "Hyperparameter search finished. Best score: %.4f", study.best_value
        )
        logger.info("Best parameters: %s", study.best_params)
        trials = []
        for t in study.trials:
            if t.value is None:
                continue

            trials.append(
                HyperparameterTrialResult(
                    trial_id=t.number,
                    model_name=model_wrapper.model_name(),
                    params=t.params,
                    score=t.value,
                    state=t.state.name,
                )
            )

        return HyperparameterSearchResult(
            dataset=dataset,
            model_name=model_wrapper.model_name(),
            best_params=study.best_params,
            best_score=study.best_value,
            trials=trials,
        )
