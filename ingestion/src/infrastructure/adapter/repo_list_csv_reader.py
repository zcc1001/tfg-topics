import csv
from typing import List

from application.ports.repo_list_reader import RepoListReaderPort
from domain.entities.entities import RepositoryInfo


class RepoListCsvReaderPort(RepoListReaderPort):

    def __init__(self, file_path: str):
        self.file_path = file_path

    def fetch_repo_list(self) -> List[RepositoryInfo]:
        repo_list = []
        try:
            with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    owner = row.get('owner')
                    name = row.get('name')
                    type = row.get('type')

                    if owner and name:
                        repo_list.append(RepositoryInfo(owner=owner.strip(), name=name.strip(), type=type.strip()))
            return repo_list
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo de entrada '{self.file_path}' no fue encontrado.")
        except Exception as e:
            raise RuntimeError(f"Error al leer el archivo CSV: {e}")
