import csv
import os
import re
import subprocess
from tempfile import TemporaryDirectory

# === CONFIGURATION ===
SEARCH_STRING = "your_search_string_here"  # Replace this
INPUT_CSV = "repos.csv"
OUTPUT_CSV = "result.csv"
ORGANIZATION = "your-org-name"             # Replace this
TOKEN = os.getenv("TOKEN")                 # Make sure this is exported

def get_latest_release_branch(repo_url):
    with TemporaryDirectory() as tmp:
        result = subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, tmp],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode != 0:
            return None, None

        subprocess.run(["git", "fetch", "--all"], cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            branches = subprocess.check_output(["git", "branch", "-r"], cwd=tmp).decode().splitlines()
        except subprocess.CalledProcessError:
            return None, None

        release_branches = [
            b.strip().split("origin/")[-1]
            for b in branches if "origin/release/" in b
        ]

        latest_branch = None
        latest_time = 0
        for branch in release_branches:
            try:
                timestamp = subprocess.check_output(
                    ["git", "log", "-1", "--format=%ct", f"origin/{branch}"],
                    cwd=tmp
                ).decode().strip()
                if int(timestamp) > latest_time:
                    latest_time = int(timestamp)
                    latest_branch = branch
            except subprocess.CalledProcessError:
                continue
        return latest_branch, tmp if latest_branch else (None, None)

def search_in_release_branch(repo_url, branch):
    matches = []
    with TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0 or not os.path.exists(os.path.join(temp_dir, ".git")):
            return []

        for root, _, files in os.walk(temp_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if SEARCH_STRING in line:
                                rel_path = os.path.relpath(filepath, temp_dir)
                                matches.append((rel_path, branch, line.strip()))
                except Exception:
                    continue
    return matches

def get_prefix(repo_name):
    match = re.match(r"^(\d+)", repo_name)
    return match.group(1) if match else repo_name

def main():
    seen_prefixes = set()
    result_rows = []

    if not TOKEN:
        print("❌ TOKEN environment variable not set.")
        return

    with open(INPUT_CSV, newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        project = row["project"]
        repo = row["repo"]
        prefix = get_prefix(repo)

        if prefix in seen_prefixes:
            continue

        print(f"🔍 Scanning latest release/* of {project}/{repo}...")

        repo_url = f"https://{TOKEN}@dev.azure.com/{ORGANIZATION}/{project}/_git/{repo}"

        release_branch, _ = get_latest_release_branch(repo_url)
        if not release_branch:
            print(f"⚠️  No release/* branches found for {repo}")
            continue

        matches = search_in_release_branch(repo_url, release_branch)

        if matches:
            seen_prefixes.add(prefix)
            for file_path, branch, matched_line in matches:
                result_rows.append({
                    "project": project,
                    "repo": repo,
                    "file_path": file_path,
                    "branch": branch,
                    "matched_line": matched_line
                })

    if result_rows:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["project", "repo", "file_path", "branch", "matched_line"])
            writer.writeheader()
            writer.writerows(result_rows)
        print(f"\n✅ Done. Results saved to {OUTPUT_CSV}")
    else:
        print("\n✅ Done. No matches found.")

if __name__ == "__main__":
    main()
