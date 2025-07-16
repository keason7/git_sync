import shutil
import subprocess
from pathlib import Path


def rsync(src, dst, verbose):
    if verbose:
        args = "-acv"
    else:
        args = "-ac"

    subprocess.run(["rsync", args, "--delete", src, dst], check=True)


def rsync_file(src, dst, verbose):
    rsync(str(src), str(dst), verbose)


def rsync_directory(src, dst, verbose):
    src, dst = str(src), str(dst)

    if not src.endswith("/"):
        src += "/"
    if not dst.endswith("/"):
        dst += "/"

    rsync(src, dst, verbose)


def create_backup(db, verbose=False):
    path_index = (db.path_repo_local / "./.tmp/").resolve()
    path_index.mkdir(mode=0o777, parents=False, exist_ok=True)

    for path_to_sync, path_synced in db.links.items():
        path_to_sync, path_synced = Path(path_to_sync), Path(path_synced)

        if path_to_sync.exists():
            path_index_sync = path_index / path_synced.name
            path_index_sync.mkdir(mode=0o777, parents=False, exist_ok=True)

            if path_to_sync.is_dir():
                rsync_directory(path_to_sync, path_index_sync, verbose=False)

            elif path_to_sync.is_file():
                rsync_file(path_to_sync, path_index_sync, verbose=False)

            else:
                print(f"Not a file or directory: {str(path_to_sync)}")

    rsync_directory(path_index, db.path_data, verbose)
    shutil.rmtree(str(path_index))
