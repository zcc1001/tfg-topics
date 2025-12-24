import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import requests

from ingestion.application.ports.github_port import GitHubPort
from ingestion.domain.entities.entities import (
    IssueData,
    ReadmeData,
    TextData,
    ThesisData,
)

logger = logging.getLogger(__name__)


class GithubRestAdapter(GitHubPort):
    BASE_URL = "https://api.github.com/repos"
    TARGET_LATEX_FILES = [
        "tex/1_Introduccion.tex",
        "tex/2_Objetivos_del_proyecto.tex",
        "tex/3_Conceptos_teoricos.tex",
        "tex/4_Tecnicas_y_herramientas.tex",
        "text/5_Aspectos_relevantes_del_desarrollo_del_proyecto.tex"
        "text/6_Trabajos_relacionados.tex"
        "tex/7_Conclusiones_Lineas_de_trabajo_futuras.tex",
    ]

    def __init__(self, token: Optional[str] = None, timeout: float = 10.0):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        self.timeout = timeout
        if token:
            self.headers["Authorization"] = f"token {token}"
            logger.info("GitHub token provided. Using authenticated requests.")
        else:
            logger.warning(
                "No GitHub token provided. Using unauthenticated requests,"
                " which have a lower rate limit."
            )
        logger.debug("HTTP requests timeout set to %s seconds", self.timeout)

    def _handle_response(
        self, response: requests.Response
    ) -> Optional[Union[dict[str, Any], list[dict[str, Any]]]]:
        if response.status_code == 200:
            return cast(Union[dict[str, Any], list[dict[str, Any]]], response.json())
        elif response.status_code == 404:
            logger.error(
                "Error: Repository %s not found (status code 404). Check the names.",
                response.url,
            )
            return None
        elif response.status_code == 403:
            logger.error(
                "Error: GitHub rate limit exceeded or invalid/insufficient "
                "Personal Access Token (status code 403)."
            )
            logger.warning(
                "Rate limit remaining: %s",
                response.headers.get("X-RateLimit-Remaining"),
            )
            return None
        else:
            logger.error("Error: %s - %s", response.status_code, response.text)
            return None

    def get_issues(self, owner: str, repo_name: str) -> List[IssueData]:
        logger.info("Getting issues for repository: %s/%s", owner, repo_name)

        url = f"{self.BASE_URL}/{owner}/{repo_name}/issues"
        page = 1
        issues = []
        while True:
            params: Dict[str, Union[str, int]] = {
                "per_page": 100,
                "page": page,
                "state": "all",
                "sort": "updated",
            }
            response = requests.get(
                url, headers=self.headers, params=params, timeout=self.timeout
            )
            json_data = self._handle_response(response)
            if not json_data:
                logger.info(
                    "No more issues found on page %s for repository: %s/%s",
                    page,
                    owner,
                    repo_name,
                )
                break

            if not isinstance(json_data, list):
                logger.warning(
                    "Expected a list of issues, but received a dict for %s/%s",
                    owner,
                    repo_name,
                )
                break

            for issue in json_data:
                if "pull_request" in issue:
                    continue
                issues.append(
                    IssueData(
                        repo_name=repo_name,
                        repo_owner=owner,
                        issue_id=int(issue.get("number", 0)),
                        title=str(issue.get("title", "")),
                        description=str(issue.get("body", "")),
                        retrieved_at=datetime.now(timezone.utc),
                    )
                )
            page += 1
        logger.info(
            "Found %s issues for repository: %s/%s", len(issues), owner, repo_name
        )
        return issues

    def get_readme(self, owner: str, repo_name: str) -> Optional[ReadmeData]:
        logger.info("Getting README for repository: %s/%s", owner, repo_name)
        url = f"{self.BASE_URL}/{owner}/{repo_name}/readme"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        json_data = self._handle_response(response)
        if (
            not json_data
            or not isinstance(json_data, dict)
            or json_data.get("content") is None
        ):
            logger.warning("README not found for repository: %s/%s", owner, repo_name)
            return None

        readme = ReadmeData(
            repo_name=repo_name,
            repo_owner=owner,
            download_url=str(json_data.get("download_url", "")),
            content=str(json_data.get("content", "")),
            retrieved_at=datetime.now(timezone.utc),
        )
        logger.info("README found for repository: %s/%s", owner, repo_name)
        return readme

    def get_thesis_data(self, owner: str, repo_name: str) -> Optional[ThesisData]:
        logger.info("Getting thesis data for repository: %s/%s", owner, repo_name)
        branch = self._get_default_branch(owner, repo_name)
        tree_paths = self._get_repo_tree(owner, repo_name, branch)

        matches = self._find_target_latex_files(tree_paths, self.TARGET_LATEX_FILES)

        list_texts = []
        for logical_path, real_path in matches.items():
            content = self._download_raw_file(
                owner=owner,
                repo=repo_name,
                branch=branch,
                path=real_path,
            )
            if content:
                list_texts.append(
                    TextData(
                        contents=content,
                        section=Path(logical_path).stem,
                    )
                )

        if not list_texts:
            logger.warning(
                "No thesis LaTeX files found for repository: %s/%s", owner, repo_name
            )
            return None

        return ThesisData(
            repo_name=repo_name,
            repo_owner=owner,
            texts=list_texts,
            retrieved_at=datetime.now(timezone.utc),
        )

    def _get_default_branch(self, owner: str, repo: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        json_data = self._handle_response(response)
        if json_data and isinstance(json_data, dict):
            return cast(str, str(json_data.get("default_branch", "main")))
        logger.error("Could not retrieve default branch for %s/%s", owner, repo)
        return "main"  # Default to 'main' if unable to retrieve

    def _get_repo_tree(self, owner: str, repo: str, branch: str) -> list[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}"
        response = requests.get(
            url,
            headers=self.headers,
            params={"recursive": "1"},
            timeout=self.timeout,
        )
        json_data = self._handle_response(response)
        if (
            json_data
            and isinstance(json_data, dict)
            and "tree" in json_data
            and isinstance(json_data["tree"], list)
        ):
            return [str(item["path"]) for item in json_data["tree"] if "path" in item]
        logger.error("Could not retrieve default branch for %s/%s", owner, repo)
        return []

    def _download_raw_file(self, owner: str, repo: str, branch: str, path: str) -> str:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        if response.status_code == 200:
            return response.text
        logger.error(
            "Failed to download raw file from %s. Status: %s",
            url,
            response.status_code,
        )
        return ""

    def _find_target_latex_files(
        self,
        tree_paths: list[str],
        target_suffixes: list[str],
    ) -> dict[str, str]:
        normalized_tree = {path.replace("\\", "/").lower(): path for path in tree_paths}
        normalized_target_suffixes = [suf.lower() for suf in target_suffixes]
        found = {}

        for norm_path, real_path in normalized_tree.items():
            for suffix in normalized_target_suffixes:
                if norm_path.endswith(suffix):
                    found[suffix] = real_path

        return found
