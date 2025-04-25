import csv
import os
import re
import subprocess
from tempfile import TemporaryDirectory

# CONFIGURE THIS
SEARCH_STRING = "your_search_string_here"  # ← replace this
INPUT_CSV = "repos.csv"
OUTPUT_CSV = "result.csv"
TOKEN = os.getenv("TOKEN")  # Expected as env var

def get_latest_release_branch(repo_path):
    subprocess.run(["git", "fetch", "--all"], cwd=repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        branches = subprocess.check_output(["git", "branch", "-r"], cwd=repo_path).decode().splitlines()
    except subprocess.CalledProcessError:
        return None

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
                cwd=repo_path
            ).decode().strip()
            if int(timestamp) > latest_time:
                latest_time = int(timestamp)
                latest_branch = branch
        except subprocess.CalledProcessError:
            continue
    return latest_branch

def search_in_repo(repo_url, branch):
    matches = []
    with TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            return []

        if not os.path.exists(os.path.join(temp_dir, ".git")):
            return []

        for root, _, files in os.walk(temp_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if SEARCH_STRING in line:
                                rel_path = os.path.relpath(filepath, temp_dir)
                                matches.append((rel_path, line_num, line.strip()))
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
        print("❌ TOKEN environment variable not set. Exiting.")
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

        print(f"🔍 Scanning {project}/{repo}...")

        repo_url = f"https://{TOKEN}@dev.azure.com/{project}/_git/{repo}"

        # Try main branch
        matches = search_in_repo(repo_url, "main")
        if matches:
            for path, line_num, line in matches:
                result_rows.append([project, repo, path, "main", SEARCH_STRING])
            seen_prefixes.add(prefix)
            continue

        # Try latest release branch
        with TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, tmp],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0 or not os.path.exists(os.path.join(tmp, ".git")):
                continue

            latest_release = get_latest_release_branch(tmp)

        if latest_release:
            matches = search_in_repo(repo_url, latest_release)
            if matches:
                for path, line_num, line in matches:
                    result_rows.append([project, repo, path, latest_release, SEARCH_STRING])
                seen_prefixes.add(prefix)

    with open(OUTPUT_CSV, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["project", "repo", "file_path", "branch", "search_string"])
        writer.writerows(result_rows)

    print(f"✅ Done. Results written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
