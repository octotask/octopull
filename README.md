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

### Workflow example

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
      - uses: octotask/octopull@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
