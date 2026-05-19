import argparse
from unittest.mock import MagicMock, patch

from processing.main import main


@patch("processing.main.argparse.ArgumentParser.parse_args")
@patch("processing.main.EnsureProcessingDatasetConsistencyUseCase")
@patch("processing.main.TopicModelingUseCase")
@patch("processing.main.configure_application_logging")
@patch("processing.main.ParquetDatasetStateAdapter")
@patch("processing.main.ParquetDocumentRepository")
@patch("processing.main.HyperparameterSearchService")
@patch("processing.main.DataParquetStorageWriter")
@patch("processing.main.nltk.download")
@patch("processing.main.LdaTopicModelAdapter")
def test_main_lda(
    mock_lda: MagicMock,
    mock_nltk: MagicMock,
    mock_writer: MagicMock,
    mock_hyper: MagicMock,
    mock_repo: MagicMock,
    mock_adapter: MagicMock,
    mock_log: MagicMock,
    mock_topic_usecase: MagicMock,
    mock_consistency: MagicMock,
    mock_args: MagicMock,
) -> None:
    mock_args.return_value = argparse.Namespace(model="lda", dataset="issues")
    mock_consistency.return_value.execute.return_value = "fake_hash"

    main()

    mock_args.assert_called_once()
    mock_log.assert_called_once()
    mock_lda.assert_called_once()
    mock_consistency.return_value.execute.assert_called_once_with(
        dataset="issues", model_name="lda"
    )
    mock_topic_usecase.return_value.execute.assert_called_once_with(dataset="issues")


@patch("processing.main.argparse.ArgumentParser.parse_args")
@patch("processing.main.EnsureProcessingDatasetConsistencyUseCase")
@patch("processing.main.TopicModelingUseCase")
@patch("processing.main.BerTopicModelAdapter")
@patch("processing.main.nltk.download")
def test_main_bertopic(
    mock_nltk: MagicMock,
    mock_bertopic: MagicMock,
    mock_topic_usecase: MagicMock,
    mock_consistency: MagicMock,
    mock_args: MagicMock,
) -> None:
    mock_args.return_value = argparse.Namespace(model="bertopic", dataset="readmes")
    mock_consistency.return_value.execute.return_value = "fake_hash"
    main()
    mock_bertopic.assert_called_once()


@patch("processing.main.argparse.ArgumentParser.parse_args")
@patch("processing.main.EnsureProcessingDatasetConsistencyUseCase")
@patch("processing.main.TopicModelingUseCase")
@patch("processing.main.Top2VecModelAdapter")
@patch("processing.main.nltk.download")
def test_main_top2vec(
    mock_nltk: MagicMock,
    mock_top2vec: MagicMock,
    mock_topic_usecase: MagicMock,
    mock_consistency: MagicMock,
    mock_args: MagicMock,
) -> None:
    mock_args.return_value = argparse.Namespace(model="top2vec", dataset="abstracts")
    mock_consistency.return_value.execute.return_value = "fake_hash"
    main()
    mock_top2vec.assert_called_once()


@patch("processing.main.argparse.ArgumentParser.parse_args")
@patch("processing.main.EnsureProcessingDatasetConsistencyUseCase")
@patch("processing.main.TopicModelingUseCase")
@patch("processing.main.FastTopicModelAdapter")
@patch("processing.main.nltk.download")
def test_main_fastopic(
    mock_nltk: MagicMock,
    mock_fastopic: MagicMock,
    mock_topic_usecase: MagicMock,
    mock_consistency: MagicMock,
    mock_args: MagicMock,
) -> None:
    mock_args.return_value = argparse.Namespace(model="fastopic", dataset="thesis")
    mock_consistency.return_value.execute.return_value = "fake_hash"
    main()
    mock_fastopic.assert_called_once()


@patch("processing.main.argparse.ArgumentParser.parse_args")
@patch("processing.main.logger")
def test_main_unsupported_model(mock_logger: MagicMock, mock_args: MagicMock) -> None:
    mock_args.return_value = argparse.Namespace(model="unsupported", dataset="issues")

    main()

    mock_logger.error.assert_called_with("Model '%s' is not supported.", "unsupported")
