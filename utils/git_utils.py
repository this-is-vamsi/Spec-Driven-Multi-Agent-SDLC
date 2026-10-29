import os
import re
import tempfile
import shutil


def _sanitize_branch_name(name: str) -> str:
    """Convert an arbitrary string into a valid git branch name."""
    name = name.replace(" ", "-")
    name = re.sub(r"[^a-zA-Z0-9/_\-.]", "", name)
    name = re.sub(r"\.{2,}", ".", name)
    name = re.sub(r"-{2,}", "-", name)
    name = name.strip("-./")
    return name or "feature/generated-stub"


def init_local_repo(project_dir: str) -> str:
    """
    Initialize a local git repository in the given directory.
    Returns the repo path.
    """
    try:
        from git import Repo

        if not os.path.exists(os.path.join(project_dir, ".git")):
            repo = Repo.init(project_dir)
            repo.index.add([f for f in _walk_files(project_dir) if not f.startswith(".git")])
            repo.index.commit("Initial commit — AI-SDLC generated project")
        return project_dir
    except ImportError:
        return project_dir


def create_branch_and_commit(project_dir: str, branch_name: str, message: str):
    """Create a new branch (or switch to it if it exists), stage all changes, and commit."""
    branch_name = _sanitize_branch_name(branch_name)
    try:
        from git import Repo

        repo = Repo(project_dir)

        # Stage all current changes first to avoid checkout conflicts
        repo.git.add(A=True)
        if repo.is_dirty(index=True):
            repo.index.commit("WIP — staging changes before branch switch")

        # Switch to branch — create if it doesn't exist
        if branch_name in [b.name for b in repo.branches]:
            repo.git.checkout(branch_name)
        else:
            repo.git.checkout("-b", branch_name)

        # Stage and commit all changes on the target branch
        repo.git.add(A=True)
        if repo.is_dirty(index=True):
            repo.index.commit(message)
    except ImportError:
        pass


def push_and_create_pr(
    project_dir: str,
    branch_name: str,
    title: str,
    body: str,
    github_token: str,
    repo_owner: str,
    repo_name: str,
    base_branch: str = "main",
) -> dict:
    """
    Push branch and open a pull request via the GitHub API.
    Returns PR URL or error info.
    """
    branch_name = _sanitize_branch_name(branch_name)
    try:
        from git import Repo
        import urllib.request
        import json

        repo = Repo(project_dir)
        # Set remote URL with token for auth
        remote_url = f"https://{github_token}@github.com/{repo_owner}/{repo_name}.git"
        if "origin" in [r.name for r in repo.remotes]:
            repo.delete_remote("origin")
        repo.create_remote("origin", remote_url)
        repo.git.push("--set-upstream", "origin", branch_name)

        # Create pull request via GitHub API
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
        pr_data = json.dumps(
            {"title": title, "body": body, "head": branch_name, "base": base_branch}
        ).encode()
        req = urllib.request.Request(
            api_url,
            data=pr_data,
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
        return {"success": True, "pr_url": result.get("html_url", ""), "pr_number": result.get("number")}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _walk_files(directory: str) -> list[str]:
    """Walk directory and return relative file paths."""
    files = []
    for root, _, filenames in os.walk(directory):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), directory)
            files.append(rel.replace("\\", "/"))
    return files
