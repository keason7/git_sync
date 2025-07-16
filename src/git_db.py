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

        # for some reason Added and Deleted are inverted in GitPython
        # D is for added files
        # A is for deleted files
        self.categories = {
            "Added": "D",
            "Deleted": "A",
            "Renamed": "R",
            "Modified": "M",
            "TypeChanged": "T",
        }

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

    def __reset_unpushed_commits(self):
        self.repo.git.reset("--hard", f"origin/{self.repo.active_branch.name}")

    def __init_links(self, paths_sync):
        self.path_links = (self.path_repo_local / "links.yml").resolve()

        if not self.path_links.exists():
            self.links = {}

        else:
            self.links = read_yml(self.path_links)

        for path in paths_sync:
            path_to_sync = Path(path).expanduser().resolve()

            if str(path_to_sync) not in self.links.keys():
                path_synced = self.path_data / f"{path_to_sync.stem}_{str(random.getrandbits(64))}"
                self.links[str(path_to_sync)] = str(path_synced)

        write_yml(self.path_links, self.links)

    def __add_untracked(self):
        self.repo.index.add(self.repo.untracked_files)

    def __add_tracked(self):
        self.repo.git.add(update=True)

    def __get_categories(self):
        diff_categories = {k: False for k in self.categories}

        diff_staged = self.repo.index.diff("HEAD")

        for tag_key, tag_value in self.categories.items():
            staged_files = diff_staged.iter_change_type(tag_value)

            if len(list(staged_files)) > 0:
                diff_categories[tag_key] = True

        diff_categories = [category for category, is_used in diff_categories.items() if is_used]
        return " ".join(diff_categories)

    def __add_categories(self, categories):
        latest_hash = self.repo.head.commit.hexsha

        self.repo.git.notes("add", "-f", "-m", categories, latest_hash)
        self.repo.git.push("origin", "refs/notes/commits")

    def __commit(self, msg):
        self.repo.index.commit(msg)

    def __push(self):
        self.repo.remotes.origin.push()

    def sync(self):
        self.__add_untracked()
        self.__add_tracked()
        categories = self.__get_categories()

        if self.repo.is_dirty(index=True, untracked_files=True):
            now = datetime.now()
            msg = f"[{now.strftime("%Y-%m-%d %H:%M:%S")}] - Automatic commit: [{categories}] files."
            self.__commit(msg)
            self.__push()

            self.__add_categories(categories)
