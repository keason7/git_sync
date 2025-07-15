import subprocess
from pathlib import Path


def create_backup(paths_sync, path_repo):
    for path_sync in paths_sync:
        path_sync = Path(path_sync).expanduser().resolve()

        if not path_sync.exists() or not path_repo.exists():
            raise ValueError("Path do not exist.")

        path_backup = path_repo / Path(path_sync).stem
        path_backup.mkdir(mode=0o777, parents=False, exist_ok=True)

        if path_sync.is_dir():
            path_sync, path_backup = str(path_sync), str(path_backup)

            if not path_sync.endswith("/"):
                path_sync += "/"
            if not path_backup.endswith("/"):
                path_backup += "/"

            rsync(path_sync, path_backup)

        elif path_sync.is_file():
            path_sync, path_backup = str(path_sync), str(path_backup)
            rsync(path_sync, path_backup)

        else:
            print("Unknown file type")


def rsync(src, dst):
    subprocess.run(["rsync", "-acv", src, dst], check=True)
