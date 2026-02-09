from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class IssueData:
    thesis_id: int
    repo_owner: str
    repo_name: str
    issue_id: int
    title: str
    description: str
    retrieved_at: datetime


@dataclass
class ReadmeData:
    thesis_id: int
    download_url: str
    content: str
    retrieved_at: datetime


@dataclass
class TextData:
    contents: str
    section: str


@dataclass
class ThesisData:
    thesis_id: int
    texts: List[TextData]
    retrieved_at: datetime


@dataclass(frozen=True)
class ThesisInfo:
    thesis_id: int
    title: str
    tutor: str
    student: str
    presentation_date: str
    assignment_date: str
    grade: str
    repository_url: str
    repo_owner: str = ""
    repo_name: str = ""
