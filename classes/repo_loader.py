import io
import requests
import zipfile


class RepoLoader:

    def __init__(self, allowed_extensions: tuple, max_archive_size: int = 1_000_000):
        self.max_archive_size = max_archive_size
        self.allowed_extensions = allowed_extensions

    def _load_repo_bytes(self,  repo_url: str, branch: str = "main"):

        # Формируем путь откуда утащим репозиторий
        download_url = f"{repo_url}/zipball/{branch}/"

        with requests.get(download_url, stream=False) as response:
            response.raise_for_status()
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_archive_size:
                raise ValueError("Размер архива превышает максимально допустимый.")

        return response.content

    def get_repo_files(self, repo_url: str, branch: str = "main") -> dict[str, str]:

        response_content = self._load_repo_bytes(repo_url, branch)
        repo_content = {}

        with zipfile.ZipFile(io.BytesIO(response_content)) as zip_ref:
            for zip_info in zip_ref.infolist():
                # берем только файлы с разрешенными расширениями
                if zip_info.filename.endswith(self.allowed_extensions):
                    with zip_ref.open(zip_info) as file:
                        # Переводим байты в строки
                        with io.TextIOWrapper(file, encoding='utf-8') as text_file:
                            # откусываем имя репозитория от относительного пути
                            file_path = "/".join(zip_info.filename.split("/")[1:])
                            repo_content[file_path] = text_file.read()

        return repo_content
