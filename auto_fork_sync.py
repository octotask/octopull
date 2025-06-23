import os
import subprocess
import sys
import tempfile
import yaml
import datetime
from github import Github, GithubException

CONFIG_FILE = ".github/pull.yml"
AUTO_CLOSE_ON_CONFLICT = False  # Set True to auto-close conflicted PRs

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Missing config: {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    success = (result.returncode == 0)
    return success, result.stdout.strip() + "\n" + result.stderr.strip()

def create_or_update_pr(gh_repo, head_branch, base_branch, strategy, config):
    # Check if a PR from this branch to base_branch exists
    pulls = gh_repo.get_pulls(state="open", head=f"{gh_repo.owner.login}:{head_branch}", base=base_branch)
    pr = pulls[0] if pulls.totalCount > 0 else None

    if not pr:
        pr = gh_repo.create_pull(
            title=f"Sync with upstream ({strategy})",
            body="This PR syncs the fork with upstream.",
            head=head_branch,
            base=base_branch
        )
        print(f"Created PR: {pr.html_url}")
    else:
        print(f"Using existing PR: {pr.html_url}")

    # Assign reviewers and assignees if configured
    assignees = config.get("assignees", [])
    if assignees:
        try:
            pr.add_to_assignees(*assignees)
        except GithubException as e:
            print(f"Warning: Could not add assignees: {e}")

    reviewers = config.get("reviewers", [])
    if reviewers:
        try:
            pr.create_review_request(reviewers)
        except GithubException as e:
            print(f"Warning: Could not add reviewers: {e}")

    return pr

def handle_conflict(pr, conflict_output):
    conflict_message = (
        "⚠️ **Conflict detected during upstream sync!**\n\n"
        "The automatic merge/rebase failed due to conflicts. "
        "Please resolve conflicts manually by pulling the branch, fixing conflicts, and pushing.\n\n"
        "### Conflict details:\n```\n" + conflict_output + "\n```"
    )
    try:
        pr.create_issue_comment(conflict_message)
        pr.add_to_labels("conflict")
        print("Posted conflict comment and added 'conflict' label.")
        if AUTO_CLOSE_ON_CONFLICT:
            pr.edit(state="closed")
            print("PR auto-closed due to conflict.")
    except GithubException as e:
        print(f"Failed to comment/label PR: {e}")

def sync_fork(config):
    repo_url = subprocess.run("git config --get remote.origin.url", shell=True, capture_output=True, text=True).stdout.strip()
    upstream_url = config['upstream']
    default_branch = config.get('default_branch', 'main')
    strategy = config.get('sync_strategy', 'merge')
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    sync_branch = f"sync-upstream-{timestamp}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone the fork repo
        run(f"git clone {repo_url} .", cwd=tmpdir)
        run(f"git remote add upstream {upstream_url}", cwd=tmpdir)
        run("git fetch upstream", cwd=tmpdir)

        # Prepare the sync branch
        if strategy in ("merge", "rebase", "squash"):
            run(f"git checkout -b {sync_branch} origin/{default_branch}", cwd=tmpdir)
        elif strategy == "hard-reset":
            # Hard reset directly to upstream branch
            run(f"git checkout -B {sync_branch} upstream/{default_branch}", cwd=tmpdir)
        else:
            print(f"Unsupported strategy: {strategy}")
            sys.exit(1)

        # Perform sync with conflict detection
        conflict_output = ""
        if strategy == "merge":
            success, output = run(f"git merge upstream/{default_branch} --no-edit", cwd=tmpdir)
            if not success:
                conflict_output = output
        elif strategy == "rebase":
            success, output = run(f"git rebase upstream/{default_branch}", cwd=tmpdir)
            if not success:
                conflict_output = output
        elif strategy == "squash":
            success, output = run(f"git merge --squash upstream/{default_branch}", cwd=tmpdir)
            if not success:
                conflict_output = output
            else:
                # Commit the squash merge
                success, output = run('git commit -m "Squash merge upstream changes"', cwd=tmpdir)
                if not success:
                    conflict_output = output
        elif strategy == "hard-reset":
            success = True  # no merge, no conflict possible
        else:
            print(f"Unsupported strategy: {strategy}")
            sys.exit(1)

        # If conflict detected, push branch anyway to create PR with conflict info
        if conflict_output:
            print("Conflict detected during sync!")
        else:
            print("Sync successful, pushing changes.")

        run(f"git push origin {sync_branch}", cwd=tmpdir)

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN env variable is required")
            sys.exit(1)

        gh = Github(token, base_url=os.getenv("GITHUB_API", "https://api.github.com"))
        gh_repo = gh.get_repo(os.getenv("GITHUB_REPOSITORY"))

        pr = create_or_update_pr(gh_repo, sync_branch, default_branch, strategy, config)

        if conflict_output:
            handle_conflict(pr, conflict_output)

if __name__ == "__main__":
    config = load_config()
    sync_fork(config)
