"""Git Database class."""

import random
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from git import Repo

from src.utils import get_hashed_machine_id, read_yml, write_yml


class GitDb:
    """GitDb class that manage data repo sync."""

    def __init__(self, config):
        """Initialize.

        Args:
            config (dict): Config dictionary.
        """
        self.repo = None
        self.credentials = config["credentials"]

        self.path_install = Path(config["path_install"]).expanduser()
        self.path_install.mkdir(mode=0o777, parents=False, exist_ok=True)

        repo_hash = sha256(f"{self.credentials["username"]}_{self.credentials["repo"]}".encode("utf-8")).hexdigest()

        self.path_repo_remote = self.__get_uri()
        self.path_repo_local = self.path_install / repo_hash / self.credentials["repo"]

        self.__clone()

        # commits categories
        # Added and Deleted are inverted in GitPython
        # D is for added files and A is for deleted files
        self.categories = {
            "Added": "D",
            "Deleted": "A",
            "Renamed": "R",
            "Modified": "M",
            "TypeChanged": "T",
        }

        # create a specific folder for each machine that is synced
        machine_id = get_hashed_machine_id()

        self.path_data = (self.path_repo_local / f"./data/{machine_id}").resolve()
        self.path_data.mkdir(mode=0o777, parents=True, exist_ok=True)

        self.__reset_unpushed_commits()
        self.__init_links(config["paths_sync"])

    def __get_uri(self):
        """Get remote git adress.

        Raises:
            ValueError: Invalid credential method.

        Returns:
            str: Git adress.
        """
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
        """Clone repository or initialize from local one."""
        if not self.path_repo_local.exists():
            self.repo = Repo.clone_from(self.path_repo_remote, self.path_repo_local)
        else:
            self.repo = Repo(self.path_repo_local)

    def __reset_unpushed_commits(self):
        """Reset local unpushed commits."""
        self.repo.git.reset("--hard", f"origin/{self.repo.active_branch.name}")

    def __init_links(self, paths_sync):
        """Initialize links dict to match paths in config to there location in ./data/.

        Args:
            paths_sync (list): List of paths to sync.
        """
        self.path_links = (self.path_data / "links.yml").resolve()

        if not self.path_links.exists():
            self.links = {}
        else:
            self.links = read_yml(self.path_links)

        for path in paths_sync:
            path_to_sync = Path(path).expanduser().resolve()

            # add link such as /path/to/folder: ./data/folder_hash/
            if str(path_to_sync) not in self.links.keys():
                path_synced = self.path_data / f"{path_to_sync.stem}_{str(random.getrandbits(64))}"
                self.links[str(path_to_sync)] = str(path_synced)

    def __add_untracked(self):
        """Add untracked files to index."""
        self.repo.index.add(self.repo.untracked_files)

    def __add_tracked(self):
        """Add tracked files to index."""
        self.repo.git.add(update=True)

    def __get_categories(self):
        """Get all changes types in staged diff to create category labels for current commit (Added, Modified, ...).

        Returns:
            str: Categories string.
        """
        diff_categories = {k: False for k in self.categories}
        diff_staged = self.repo.index.diff("HEAD")

        for category_key, category_value in self.categories.items():
            staged_files = diff_staged.iter_change_type(category_value)

            if len(list(staged_files)) > 0:
                diff_categories[category_key] = True

        diff_categories = [category for category, is_used in diff_categories.items() if is_used]

        # Return categories string such as "Added Modified"
        return " ".join(diff_categories)

    def __add_categories(self, categories):
        """Add categories notes to latest commit.

        Args:
            categories (str): Categories string.
        """
        latest_hash = self.repo.head.commit.hexsha

        # fetch remote notes first
        self.repo.git.fetch("origin", "refs/notes/*:refs/notes/*")

        self.repo.git.notes("add", "-f", "-m", categories, latest_hash)
        self.repo.git.push("origin", "refs/notes/commits")

    def __commit(self, msg):
        """Commit to data repository.

        Args:
            msg (str): Commit message.
        """
        self.repo.index.commit(msg)

    def __push(self):
        """Push commit."""
        self.repo.remotes.origin.push()

    def sync(self):
        """Synchronize paths to sync with remote data directory."""
        write_yml(self.path_links, self.links)
        self.__add_untracked()
        self.__add_tracked()
        categories = self.__get_categories()

        # check if there are staged files in index
        if self.repo.is_dirty(index=True, untracked_files=True):
            now = datetime.now()
            msg = f"[{now.strftime("%Y-%m-%d %H:%M:%S")}] - Automatic commit: [{categories}] files."

            self.__commit(msg)
            self.__push()
            self.__add_categories(categories)
