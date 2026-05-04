import logging
from pathlib import Path

import pandas as pd
import pytest

from ingestion.domain.entities.entities import ThesisInfo
from ingestion.infrastructure.adapter import repo_list_csv_reader


def test_fetch_repo_list_valid_rows(tmp_path: Path) -> None:
    """Verify CSV parsing: extracting owner/repo from URL and handling fields."""
    csv_content = (
        "title,tutors,students,assignment_date,presentation_date,grade,repository_url\n"
        "GII_O_MC_16.N Aplicación para la gestión del sonido en un dispositivo móvil,"
        "César Represa,1,02/02/2017,09/02/2018,4,"
        "https://github.com/JorgeZamora94/TFG-Jorge-Zamora-2017-18\n"
        "GII_O_MC_17.02 Sistema de navegación semiautomático en interiores,"
        '"Alejandro Merino Gómez, César García Osorio, José Francisco Díez Pastor",'
        "1,09/11/2017,05/06/2018,10,"
        "https://github.com/mbm0089/GII_0_17.02_SNSI/\n"
        "GII_O_MA_17.01 Desarrollo de una interfaz para planta piloto,"
        '"Alejandro Merino Gómez, Daniel Sarabia Ortiz",'
        "1,30/10/2018,19/02/2019,8,"
        "https://github.com/FranBurgos/TFG\n"
    )
    path = tmp_path / "tfg_list.csv"
    path.write_text(csv_content, encoding="utf-8")

    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(path))
    repos = reader.fetch_repo_list()

    assert len(repos) == 3
    assert isinstance(repos[0], ThesisInfo)
    assert repos[0].repo_owner == "JorgeZamora94"
    assert repos[0].repo_name == "TFG-Jorge-Zamora-2017-18"
    assert "Aplicación para la gestión" in repos[0].title

    assert repos[1].repo_owner == "mbm0089"
    assert repos[1].repo_name == "GII_0_17.02_SNSI"

    assert repos[2].repo_owner == "FranBurgos"
    assert repos[2].repo_name == "TFG"


def test_fetch_repo_list_file_not_found() -> None:
    """Ensure a FileNotFoundError is raised for a missing CSV file."""
    missing = Path("nonexistent-file.csv")
    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(missing))
    with pytest.raises(FileNotFoundError) as exc:
        reader.fetch_repo_list()

    assert str(missing) in str(exc.value)


def test_fetch_repo_list_raises_value_error_on_parser_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Raise ValueError when pd.read_csv raises a ParserError."""
    path = tmp_path / "repos.csv"
    path.write_text("invalid,csv\n", encoding="utf-8")

    def bad_read_csv(*args: object, **kwargs: object) -> None:
        raise pd.errors.ParserError("boom")

    monkeypatch.setattr(repo_list_csv_reader.pd, "read_csv", bad_read_csv)

    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(path))
    with pytest.raises(ValueError) as exc:
        reader.fetch_repo_list()

    assert "Malformed CSV file" in str(exc.value)


def test_fetch_repo_list_skips_invalid_url(tmp_path: Path) -> None:
    """Rows with invalid/unsupported repository URLs are skipped with a warning."""
    csv_content = (
        "title,tutors,students,assignment_date,presentation_date,grade,repository_url\n"
        "Valid thesis,Tutor A,1,01/01/2020,01/06/2020,7,"
        "https://github.com/owner/repo\n"
        "Invalid URL thesis,Tutor B,1,01/01/2020,01/06/2020,8,"
        "https://github.com/vrt0004\n"
        "Another valid thesis,Tutor C,1,01/01/2020,01/06/2020,9,"
        "https://github.com/owner2/repo2\n"
    )
    path = tmp_path / "tfg_list.csv"
    path.write_text(csv_content, encoding="utf-8")

    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(path))
    repos = reader.fetch_repo_list()

    assert len(repos) == 2
    assert repos[0].repo_owner == "owner"
    assert repos[0].repo_name == "repo"
    assert repos[1].repo_owner == "owner2"
    assert repos[1].repo_name == "repo2"


def test_fetch_repo_list_skips_invalid_url_logs_warning(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A warning is logged when a row with an invalid URL is skipped."""
    csv_content = (
        "title,tutors,students,assignment_date,presentation_date,grade,repository_url\n"
        "Invalid URL thesis,Tutor B,1,01/01/2020,01/06/2020,8,"
        "https://github.com/vrt0004\n"
    )
    path = tmp_path / "tfg_list.csv"
    path.write_text(csv_content, encoding="utf-8")

    reader = repo_list_csv_reader.RepoListCsvReaderPort(str(path))
    with caplog.at_level(logging.WARNING):
        repos = reader.fetch_repo_list()

    assert len(repos) == 0
    assert any("vrt0004" in record.message for record in caplog.records)
