"""
Test GitHub PR Connection
==========================
Validates that the GitHub token can authenticate, access the repo,
and create/close a test PR successfully.

Usage:
    python -m test_scripts.test_github_connection
"""

import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_OWNER = os.getenv("GITHUB_REPO_OWNER", "")
GITHUB_REPO = os.getenv("GITHUB_REPO_NAME", "")
BASE_BRANCH = os.getenv("GITHUB_BASE_BRANCH", "main")


def _api_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make an authenticated GitHub API request."""
    url = f"https://api.github.com{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def test_token_auth():
    """Test 1: Verify the GitHub token is valid and can authenticate."""
    print("=" * 60)
    print("TEST 1: GitHub Token Authentication")
    print("=" * 60)
    try:
        user = _api_request("GET", "/user")
        print(f"  ✅ PASS — Authenticated as: {user.get('login')}")
        print(f"     Name: {user.get('name', 'N/A')}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ❌ FAIL — HTTP {e.code}: {e.reason}")
        if e.code == 401:
            print("     → Token is invalid or expired. Update GITHUB_TOKEN in .env")
        return False


def test_repo_access():
    """Test 2: Verify access to the configured repository."""
    print("\n" + "=" * 60)
    print(f"TEST 2: Repository Access — {GITHUB_OWNER}/{GITHUB_REPO}")
    print("=" * 60)
    try:
        repo = _api_request("GET", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}")
        print(f"  ✅ PASS — Repo found: {repo.get('full_name')}")
        print(f"     Default branch: {repo.get('default_branch')}")
        print(f"     Private: {repo.get('private')}")
        perms = repo.get("permissions", {})
        print(f"     Permissions: push={perms.get('push')}, admin={perms.get('admin')}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ❌ FAIL — HTTP {e.code}: {e.reason}")
        if e.code == 404:
            print(f"     → Repo '{GITHUB_OWNER}/{GITHUB_REPO}' not found or token lacks access")
        return False


def test_create_and_close_pr():
    """Test 3: Create a test branch, push, create PR, and close it."""
    print("\n" + "=" * 60)
    print("TEST 3: Create & Close Test PR")
    print("=" * 60)

    branch_name = "test/ai-sdlc-connection-test"

    try:
        # Get the SHA of the base branch
        ref = _api_request("GET", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/ref/heads/{BASE_BRANCH}")
        base_sha = ref["object"]["sha"]
        print(f"  📌 Base branch '{BASE_BRANCH}' SHA: {base_sha[:8]}...")

        # Create a test branch via API
        try:
            _api_request("POST", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/refs", {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            })
            print(f"  🔀 Created branch: {branch_name}")
        except urllib.error.HTTPError as e:
            if e.code == 422:
                print(f"  ℹ️  Branch '{branch_name}' already exists — reusing")
            else:
                raise

        # Create a test file on the branch
        import base64
        content = base64.b64encode(
            b"# AI-SDLC Connection Test\nThis file was created by the automated PR test.\n"
        ).decode()
        try:
            _api_request("PUT", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/test_connection.md", {
                "message": "test: AI-SDLC connection verification",
                "content": content,
                "branch": branch_name,
            })
            print("  📝 Created test file on branch")
        except urllib.error.HTTPError:
            # File might already exist, try updating
            try:
                existing = _api_request(
                    "GET",
                    f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/test_connection.md?ref={branch_name}",
                )
                _api_request("PUT", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/test_connection.md", {
                    "message": "test: AI-SDLC connection verification (update)",
                    "content": content,
                    "branch": branch_name,
                    "sha": existing["sha"],
                })
                print("  📝 Updated test file on branch")
            except Exception:
                print("  ⚠️  Could not create/update test file — continuing anyway")

        # Create PR
        pr = _api_request("POST", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/pulls", {
            "title": "[TEST] AI-SDLC Connection Verification",
            "body": "Automated test PR from AI-SDLC Accelerator.\n\nThis PR will be closed immediately.",
            "head": branch_name,
            "base": BASE_BRANCH,
        })
        pr_number = pr["number"]
        pr_url = pr["html_url"]
        print(f"  ✅ PR created: #{pr_number} — {pr_url}")

        # Close the PR
        _api_request("PATCH", f"/repos/{GITHUB_OWNER}/{GITHUB_REPO}/pulls/{pr_number}", {
            "state": "closed",
        })
        print(f"  🔒 PR #{pr_number} closed successfully")

        # Delete the test branch
        try:
            url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/refs/heads/{branch_name}"
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json",
                },
                method="DELETE",
            )
            urllib.request.urlopen(req)
            print(f"  🗑️  Branch '{branch_name}' deleted")
        except Exception:
            print(f"  ⚠️  Could not delete branch '{branch_name}' — clean up manually")

        print(f"\n  ✅ PASS — Full PR lifecycle works!")
        return True

    except urllib.error.HTTPError as e:
        body = e.read().decode() if hasattr(e, "read") else ""
        print(f"  ❌ FAIL — HTTP {e.code}: {e.reason}")
        if body:
            try:
                err = json.loads(body)
                print(f"     Message: {err.get('message', body)}")
            except json.JSONDecodeError:
                print(f"     Body: {body[:200]}")
        return False
    except Exception as e:
        print(f"  ❌ FAIL — {e}")
        return False


def main():
    print("\n🔗 AI-SDLC — GitHub Connection Test Suite")
    print("=" * 60)
    print(f"  Owner: {GITHUB_OWNER}")
    print(f"  Repo:  {GITHUB_REPO}")
    print(f"  Base:  {BASE_BRANCH}")
    print(f"  Token: {'***' + GITHUB_TOKEN[-4:] if len(GITHUB_TOKEN) > 4 else '(not set)'}")
    print()

    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN not set in .env — cannot proceed.")
        sys.exit(1)
    if not GITHUB_OWNER or not GITHUB_REPO:
        print("❌ GITHUB_REPO_OWNER or GITHUB_REPO_NAME not set in .env — cannot proceed.")
        sys.exit(1)

    results = {}
    results["auth"] = test_token_auth()

    if results["auth"]:
        results["repo"] = test_repo_access()
    else:
        results["repo"] = False
        print("\n  ⏭️  Skipping repo test — auth failed")

    if results["repo"]:
        results["pr"] = test_create_and_close_pr()
    else:
        results["pr"] = False
        print("\n  ⏭️  Skipping PR test — repo access failed")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    print(f"\n  Result: {passed}/{total} tests passed")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
