# gitsync

Perform data sync from remote computer to git repository.

## Install

- Clone gitsync repository.

  ```bash
  git clone {gitsync_git_url}
  cd gitsync/
  ```

- Install and activate environment.

  ```bash
  conda env create -f environment.yml
  conda activate gitsync
  ```

- Create a private repository to host your data.

## Usage

Edit gitsync config file.

```yaml
credentials:
  username: "user_name"
  repo: "repository_name"
  method: "ssh"
  github_token: null

path_install: "~/.gitsync/"

paths_sync:
  - /path/to/folder/to/sync/
  - /path/to/file/to/sync
```

Run sync.

```bash
python sync.py
```

Files and folders in `paths_sync` will be copied to a locally installed data private repository. Any change in source data (remove file, new file, modified file, ...) will be synced to target remote data repository.

## Labels

Each commit has label(s) in the commit message and its git notes. Users can use CLI to retrieve particular commits with specific categories.

Commit categories:

```txt
Added: Added file.
Deleted: Deleted file.
Renamed: Renamed file.
Modified: Modified file.
TypeChanged: File type changed (regular file, symbolic link or submodule)
```

Show latest commit notes on the current branch.

```bash
git notes show
```

Show commits with notes on the current branch.

```bash
git notes list
```

Print all commits hash and notes where the category label "Added" is in the notes.

```bash
git log --pretty=format:"%H %s" | while read commit msg; do
  note=$(git notes show "$commit" 2>/dev/null)
  if echo "$note" | grep -q "Added"; then
    echo "$commit $msg: $note"
  fi
done
```
