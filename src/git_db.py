import random
from datetime import datetime
from pathlib import Path

from git import Repo

from src.utils import read_yml, write_yml


class GitDb:
    def __init__(self, config):
        self.repo = None
        self.credentials = config["credentials"]

        self.path_install = Path(config["path_install"]).expanduser()
        self.path_install.mkdir(mode=0o777, parents=False, exist_ok=True)

        self.path_repo_remote = self.__get_uri()
        self.path_repo_local = self.path_install / self.credentials["repo"]

        self.__clone()

        self.path_data = (self.path_repo_local / "./data/").resolve()
        self.path_data.mkdir(mode=0o777, parents=False, exist_ok=True)

        self.__reset_unpushed_commits()
        self.__init_links(config["paths_sync"])

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

    def __init_links(self, paths_sync):
        self.path_links = (self.path_repo_local / "links.yml").resolve()

        if not self.path_links.exists():
            self.links = {}

        else:
            self.links = read_yml(self.path_links)

        for path in paths_sync:
            path_to_sync = Path(path).expanduser().resolve()

            if str(path_to_sync) not in self.links.keys():
                path_synced = self.path_data / str(random.getrandbits(128))
                path_synced.mkdir(mode=0o777, parents=False, exist_ok=True)

                self.links[str(path_to_sync)] = str(path_synced)

        write_yml(self.path_links, self.links)

    def __reset_unpushed_commits(self):
        self.repo.git.reset("--hard", f"origin/{self.repo.active_branch.name}")

    def __add_untracked(self):
        self.repo.index.add(self.repo.untracked_files)

    def __add_tracked(self):
        self.repo.git.add(update=True)

    def __commit(self, msg):
        self.repo.index.commit(msg)

    def __push(self):
        self.repo.remotes.origin.push()

    def sync(self):
        self.__add_untracked()
        self.__add_tracked()

        if self.repo.is_dirty(index=True, untracked_files=True):
            now = datetime.now()
            msg = f"[{now.strftime("%Y-%m-%d %H:%M:%S")}] Automatic commit: Update gitdata."
            self.__commit(msg)
            self.__push()
