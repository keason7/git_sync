"""Backup functions modules."""

import shutil
import subprocess
from pathlib import Path


def rsync(src, dst, verbose):
    """Run rsync command with subprocess.

    Args:
        src (str): Source path.
        dst (str): Destination path.
        verbose (bool): Catch rsync terminal output.
    """
    # rsync args
    # -a : archive mode, which preserves symbolic links, permissions, timestamps, and recursively copies directories
    # -c : compares files using checksums determining whether to copy a file
    # -v : catch rsync terminal output
    if verbose:
        args = "-acv"
    else:
        args = "-ac"

    # --delete removes files from the destination that no longer exist in the source
    subprocess.run(["rsync", args, "--delete", src, dst], check=True)


def rsync_file(src, dst, verbose):
    """Run rsync for a file.

    Args:
        src (str): Source path.
        dst (str): Destination path.
        verbose (bool): Catch rsync terminal output.
    """
    rsync(str(src), str(dst), verbose)


def rsync_directory(src, dst, verbose):
    """Run rsync for a directory.

    Args:
        src (str): Source path.
        dst (str): Destination path.
        verbose (bool): Catch rsync terminal output.
    """
    src, dst = str(src), str(dst)

    # add / to copy src content within dst directory
    if not src.endswith("/"):
        src += "/"
    if not dst.endswith("/"):
        dst += "/"

    rsync(src, dst, verbose)


def create_backup(db, verbose=False):
    """Create backup to sync current state. Rsync each files/folders into a ./tmp/ folder.
    This enable to create the same directory structure as in ./data/ in order to enable
    mirror rsync. Missing source files are not copied in ./tmp/, missing source root folder are
    not copied in ./tmp/, missing files within a source folder are not copied in ./tmp/.

    Args:
        db (gitDb): Git database object.
        verbose (bool, optional): Catch rsync terminal output. Defaults to False.
    """
    # create a temprary directory in repository
    path_index = (db.path_repo_local / "./.tmp/").resolve()
    path_index.mkdir(mode=0o777, parents=False, exist_ok=True)

    # iterate over paths to sync and associated paths in data directory
    for path_to_sync, path_synced in db.links.items():
        path_to_sync, path_synced = Path(path_to_sync), Path(path_synced)

        if path_to_sync.exists():
            # create a temporary folder to copy input path_to_sync
            path_index_sync = path_index / path_synced.name
            path_index_sync.mkdir(mode=0o777, parents=False, exist_ok=True)

            if path_to_sync.is_dir():
                rsync_directory(path_to_sync, path_index_sync, verbose=False)

            elif path_to_sync.is_file():
                rsync_file(path_to_sync, path_index_sync, verbose=False)

            else:
                print(f"Not a file or directory: {str(path_to_sync)}")

    # rsync the tmp/ directory to data/ to apply the --delete
    rsync_directory(path_index, db.path_data, verbose)

    # remove tmp/ folder
    shutil.rmtree(str(path_index))
