import subprocess
from pathlib import Path


def create_backup(db, verbose=False):
    for path_to_sync, path_synced in db.links.items():
        path_to_sync, path_synced = Path(path_to_sync), Path(path_synced)

        if path_to_sync.exists() and path_synced.exists():
            if path_to_sync.is_dir():
                path_to_sync, path_synced = str(path_to_sync), str(path_synced)

                if not path_to_sync.endswith("/"):
                    path_to_sync += "/"
                if not path_synced.endswith("/"):
                    path_synced += "/"

                rsync(path_to_sync, path_synced, verbose)

            elif path_to_sync.is_file():

                rsync(str(path_to_sync), str(path_synced), verbose)

            else:
                print("Unknown file type")


def rsync(src, dst, verbose):
    if verbose:
        args = "-acv"
    else:
        args = "-ac"

    subprocess.run(["rsync", args, src, dst], check=True)
