from pydantic import BaseModel, validator
from typing import (
    Union,
    List,
    Dict,
    Any,
    ClassVar
)

from pathlib import Path
import requests
import sys
import os

class UpdateError(Exception):
    pass

class VersionModel(BaseModel):
    version: Union[float, int]

    @validator("version", pre=True, always=True)
    def validate_version(cls, v: Any) -> Union[float, int]:
        if isinstance(v, str):
            return float(v) if '.' in v else int(v)

        return v

class Updater:
    REPO: ClassVar[str] = "https://api.github.com/repos/alluding/hades/contents/"
    RAW: ClassVar[str] = "https://raw.githubusercontent.com/alluding/hades/main/"
    UPDATE: ClassVar[str] = f"{RAW}update.json"
    TO_IGNORE: ClassVar[set[str]] = {"README.md"}

    def __init__(self, current_version: Union[float, int, str]):
        self.current: Union[float, int] = VersionModel(
            version=current_version
        ).version

    @staticmethod
    def latest() -> Union[float, int]:
        response = requests.get(Updater.UPDATE)
        response.raise_for_status()

        return float(response.json().get("version"))

    @staticmethod
    def fetch(repo_url: str) -> List[Dict[str, Any]]:
        response = requests.get(repo_url)
        response.raise_for_status()

        return response.json()

    @staticmethod
    def download(url: str, path: Path) -> None:
        response = requests.get(url)
        response.raise_for_status()
        path.write_bytes(response.content)

    def has_update(self) -> bool:
        return (latest := self.latest()) > self.current

    def replace_files(
        self,
        repo_files: List[Dict[str, Any]],
        base_path: Path = Path(".")
    ) -> None:
        update_config: bool = requests.get(self.UPDATE).json().get("update_config", False)

        for file_info in repo_files:
            if file_info["name"] in self.TO_IGNORE or (file_info["name"] == "config.json" and not update_config):
                continue

            path: str = base_path / file_info["path"]

            if file_info["type"] == "file":
                self.download(f'{self.RAW}{file_info["path"]}', path)

            elif file_info["type"] == "dir":
                path.mkdir(parents=True, exist_ok=True)
                self.replace_files(
                    self.fetch(
                        file_info["_links"]["self"]
                    ),
                    base_path
                )

    def restart(self) -> None:
        os.execv(sys.executable, ["python"] + sys.argv)

    def run(self) -> None:
        if self.has_update():
            print("[HADES UPDATER] An update is available. Updating...")
            self.replace_files(self.fetch(self.REPO))
            print("[HADES UPDATER] Update completed. Restarting application...")

            self.current = self.latest()
            self.restart()
        else:
            print("[HADES UPDATER] No update available.")
