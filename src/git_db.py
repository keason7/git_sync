from pathlib import Path

from git import Repo


class GitDb:
    def __init__(self, config):
        self.credentials = config["credentials"]

        self.path_install = Path(config["path_install"]).expanduser()
        self.path_install.mkdir(mode=0o777, parents=False, exist_ok=True)

        self.__clone(self.path_install)

    def __get_uri(self):
        valid_methods = ["ssh", "https"]

        if self.credentials["method"] == "ssh":
            return f"git@github.com:{self.credentials["username"]}/{self.credentials["repo"]}.git"

        if self.credentials["method"] == "https":
            return (
                f"https://{self.credentials["username"]}:{self.credentials["github_token"]}@github.com/"
                f"{self.credentials["username"]}/{self.credentials["repo"]}.git"
            )

        else:
            raise ValueError(f"Invalid credential method. Valid protocols are: {valid_methods}.")

    def __clone(self, path):
        path_remote = self.__get_uri()
        path_local = path / self.credentials["repo"]

        if not path_local.exists():
            Repo.clone_from(path_remote, path_local)
