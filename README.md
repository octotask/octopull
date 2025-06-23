# 🚀 OctoPull

**Automate synchronization of your forked GitHub repositories with upstream projects — effortless, configurable, and reliable.**

---

![GitHub Marketplace](https://img.shields.io/badge/Marketplace-GitHub-blue?logo=github)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)

---

## ✨ Features

- 🔄 Keep your fork in sync automatically with upstream changes  
- ⚙️ Flexible merge strategies: `merge`, `rebase`, `squash`, and `hard-reset`  
- ⏰ Schedule daily updates or trigger manually  
- 👥 Auto-assign reviewers and assignees on Pull Requests  
- 🏢 Fully compatible with GitHub Enterprise Server  
- 📦 Easy to integrate into existing workflows  

---

## ⚙️ Usage

### Workflow example with OctoPull Action

```yaml
name: Sync Fork

on:
  schedule:
    - cron: '0 3 * * *'  # every day at 3 AM UTC
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: your-username/octopull@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
````

---

### Configuration

Configure `.github/pull.yml` to specify which branches to sync and how:

```yaml
sync_strategy: rebase             # merge, rebase, squash, or hard-reset
default_branch: main              # fallback branch if no branches_to_sync specified
branches_to_sync:
  - main
  - develop
  - release/v1.0
upstream: https://github.com/original/repo.git
assignees:
  - your-username
reviewers:
  - reviewer1
```

* If `branches_to_sync` is omitted or empty, only `default_branch` is synced.
* PRs will be created per branch with titles like:
  `Sync with upstream (branch: develop, strategy: rebase)`.
* Conflicts are detected per branch, with automated comments, labels, and optional auto-close.

---

### Conflict Handling

* If merge/rebase conflicts occur during sync, OctoPull will:

  * Post detailed comments on the PR with conflict info.
  * Add a `conflict` label to the PR.
  * Optionally close the PR automatically if configured.
* This keeps your fork clean and maintainers informed.

````

---

## Updated `.github/workflows/auto-sync.yml` (multi-branch aware)

```yaml
name: Auto Sync Fork

on:
  schedule:
    - cron: '0 3 * * *'  # daily at 3am UTC
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run OctoPull sync
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        run: |
          python auto_fork_sync.py
````
