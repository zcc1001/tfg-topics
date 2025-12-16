import logging
from datetime import timezone, datetime
from typing import List, Optional

import requests

from application.ports.github_port import GitHubPort
from domain.entities.entities import IssueData, ReadmeData

logger = logging.getLogger(__name__)


class GithubRestAdapter(GitHubPort):
    BASE_URL = "https://api.github.com/repos"

    def __init__(self, token: Optional[str] = None):
        self.HEADERS = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.HEADERS["Authorization"] = f"token {token}"
            logger.info("GitHub token provided. Using authenticated requests.")
        else:
            logger.warning("No GitHub token provided. Using unauthenticated requests, which have a lower rate limit.")

    def _handle_response(self, response: requests.Response):
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.error(f"Error: Repository '{response.url}' not found (status code 404). Check the names.")
            return None
        elif response.status_code == 403:
            logger.error(
                "Error: GitHub rate limit exceeded or invalid/insufficient Personal Access Token (status code 403).")
            logger.warning(f"Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
            return None
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
            return None

    def get_issues(self, owner: str, repo_name: str) -> List[IssueData]:
        logger.info(f"Getting issues for repository: {owner}/{repo_name}")
        url = f"{self.BASE_URL}/{owner}/{repo_name}/issues"
        page = 1
        issues = []
        while True:
            # CORRECCIÓN: Cambiado 'type' por 'state'
            params = {"per_page": 100, "page": page, "state": "all", "sort": "updated"}
            response = requests.get(url, headers=self.HEADERS, params=params)
            json_data = self._handle_response(response)
            if not json_data:
                logger.info(f"No more issues found on page {page} for repository: {owner}/{repo_name}")
                break
            for issue in json_data:
                if 'pull_request' in issue:
                    continue
                issues.append(
                    IssueData(repo_name=repo_name, repo_owner=owner, issue_id=issue.get("number"),
                              title=issue.get("title"), description=issue.get("body"),
                              retrieved_at=datetime.now(timezone.utc)))
            page += 1
        logger.info(f"Found {len(issues)} issues for repository: {owner}/{repo_name}")
        return issues

    def get_readme(self, owner: str, repo_name: str) -> ReadmeData:
        logger.info(f"Getting README for repository: {owner}/{repo_name}")
        url = f"{self.BASE_URL}/{owner}/{repo_name}/readme"
        response = requests.get(url, headers=self.HEADERS)
        json_data = self._handle_response(response)
        if not json_data:
            logger.warning(f"README not found for repository: {owner}/{repo_name}")
            return None

        readme = ReadmeData(repo_name=repo_name, repo_owner=owner, download_url=json_data.get("download_url"),
                            content=json_data.get("content"), retrieved_at=datetime.now(timezone.utc))
        logger.info(f"README found for repository: {owner}/{repo_name}")
        return readme
