from src.git_db import GitDb
from src.utils import read_yml


def main():
    config = read_yml("./.config.yml")
    git_db = GitDb(config)


if __name__ == "__main__":
    main()
