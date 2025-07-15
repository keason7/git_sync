from pathlib import Path

from git import Repo


class GitDb:
    def __init__(self, config):
        self.repo = None
        self.credentials = config["credentials"]

        self.path_install = Path(config["path_install"]).expanduser()
        self.path_install.mkdir(mode=0o777, parents=False, exist_ok=True)

        self.path_repo_remote = self.__get_uri()
        self.path_repo_local = self.path_install / self.credentials["repo"]

        self.__clone()

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

    def __clone(self):
        if not self.path_repo_local.exists():
            self.repo = Repo.clone_from(self.path_repo_remote, self.path_repo_local)
        else:
            self.repo = Repo(self.path_repo_local)
