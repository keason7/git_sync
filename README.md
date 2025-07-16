# git_sync

Perform data sync from remote computer to git repository

## Install

## Usage

Show latest commit notes

```bash
git notes show
```

Show commits with notes.

```bash
git notes list
```

Commit categories:

```txt
Added
Deleted
Renamed
Modified
TypeChanged
```

Print all commits and notes where the word "Added" is in the notes.

```bash
git log --pretty=format:"%H %s" | while read commit msg; do
  note=$(git notes show "$commit" 2>/dev/null)
  if echo "$note" | grep -q "Added"; then
    echo "$commit $msg: $note"
  fi
done
```
