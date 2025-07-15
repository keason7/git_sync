from src.backup import create_backup
from src.git_db import GitDb
from src.utils import read_yml


def main():
    config = read_yml("./.config.yml")
    git_db = GitDb(config)

    create_backup(git_db)


if __name__ == "__main__":
    main()
