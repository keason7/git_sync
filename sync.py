"""Sync entry script."""

import argparse

from src.backup import create_backup
from src.git_db import GitDb
from src.utils import read_yml


def sync(path_config):
    """Synchronize list paths to target remote data repository.

    Args:
        path_config (str): Config path.
    """
    config = read_yml(path_config)
    git_db = GitDb(config)

    create_backup(git_db, verbose=True)
    git_db.sync()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run bulk compression.")

    parser.add_argument(
        "-pc",
        "--path_config",
        type=str,
        default="./config.yml",
        help="Path of config file.",
    )

    args = parser.parse_args()
    sync(args.path_config)
