import os
import csv
import tempfile
import shutil
import re
from git import Repo
from concurrent.futures import ThreadPoolExecutor
import threading

# === CONFIG ===
ADO_ORG = "your-org"  # <-- Replace with your ADO org
SPECIFIC_PROJECT = "YourProject"  # <-- Replace with the exact project to filter
SEARCH_STRING = "your_search_string"  # <-- Keyword to look for
INPUT_CSV = "repos.csv"
OUTPUT_DIR = "results/scan"
THREADS = 5

# === AUTH ===
PAT = os.getenv("ADO_PAT")
if not PAT:
    raise Exception("ADO_PAT environment variable is not set.")

# === SHARED STATE ===
found_prefixes = set()
skipped_prefixes = set()  # Set to track skipped prefixes
lock = threading.Lock()

def get_repo_prefix(repo_name):
    match = re.match(r'^([a-zA-Z0-9]+)[-_\.]?', repo_name)
    result = match.group(1) if match else repo_name[:7]
    print(f"[DEBUG] Repo: {repo_name} => Prefix: {result}")
    return result

def get_default_branch(repo_path):
    try:
        return Repo(repo_path).active_branch.name
    except:
        head_ref = Repo(repo_path).git.symbolic_ref("HEAD")
        return head_ref.split("/")[-1]

def clone_and_search(project, repo_name):
    prefix = get_repo_prefix(repo_name)

    with lock:
        if prefix in found_prefixes or prefix in skipped_prefixes:
            print(f"[SKIPPED] {repo_name} (prefix {prefix} already found or skipped)")
            return

    remote_url = f"https://{PAT}@dev.azure.com/{ADO_ORG}/{project}/_git/{repo_name}"
    workdir = tempfile.mkdtemp()

    try:
        print(f"[CLONING] {project}/{repo_name}")
        repo_path = os.path.join(workdir, repo_name)
        repo = Repo.clone_from(remote_url, repo_path)

        # Check for release or main branch
        branches = [branch.name for branch in repo.branches]
        release_branch = next((branch for branch in branches if "release" in branch), None)
        main_branch = next((branch for branch in branches if "main" in branch), None)

        print(f"[BRANCHES] {repo_name} => Release: {release_branch}, Main: {main_branch}")

        # Check release branch first
        if release_branch:
            print(f"[RELEASE BRANCH] Found: {release_branch}")
            repo.git.checkout(release_branch)
            found_in_release = False
            # Search files in release branch
            for root, _, files in os.walk(repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if SEARCH_STRING in line:
                                    rel_path = os.path.relpath(file_path, repo_path)
                                    row = [project, repo_name, rel_path, i, release_branch]
                                    print(f"    [FOUND] {rel_path}:{i}")
                                    write_result(prefix, row)
                                    publish_artifact(prefix)
                                    with lock:
                                        found_prefixes.add(prefix)
                                    return
                    except Exception as e:
                        print(f"    [ERROR] reading {file_path}: {e}")
            if not found_in_release:
                print(f"[NO MATCH] No value found in release branch {repo_name}")
                write_result(prefix, [project, repo_name, "N/A", "N/A", release_branch])

        else:
            print(f"[NO RELEASE BRANCH] {repo_name} - No release branch found.")

        # Now check for main branch
        if main_branch:
            print(f"[MAIN BRANCH] Found: {main_branch}")
            repo.git.checkout(main_branch)
            found_in_main = False
            # Search files in main branch
            for root, _, files in os.walk(repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if SEARCH_STRING in line:
                                    rel_path = os.path.relpath(file_path, repo_path)
                                    row = [project, repo_name, rel_path, i, main_branch]
                                    print(f"    [FOUND] {rel_path}:{i}")
                                    write_result(prefix, row)
                                    publish_artifact(prefix)
                                    with lock:
                                        found_prefixes.add(prefix)
                                    return
                    except Exception as e:
                        print(f"    [ERROR] reading {file_path}: {e}")
            if not found_in_main:
                print(f"[NO MATCH] No value found in main branch {repo_name}")
                write_result(prefix, [project, repo_name, "N/A", "N/A", main_branch])

        print(f"  [NO MATCH] {project}/{repo_name}")

        # After processing the repo, if we find a match, skip other repos starting with the same prefix
        if prefix not in found_prefixes:
            with lock:
                skipped_prefixes.add(prefix)

    except Exception as e:
        print(f"[ERROR] {project}/{repo_name}: {e}")
    finally:
        shutil.rmtree(workdir)

def write_result(prefix, row):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, f"{prefix}_results.csv")
    write_header = not os.path.exists(csv_path)

    try:
        with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["Project", "Repo", "File Path", "Line Number", "Branch"])
            writer.writerow(row)
        print(f"[SAVED] Result written to {csv_path}")
    except Exception as e:
        print(f"[ERROR] Could not write to {csv_path}: {e}")

def publish_artifact(prefix):
    csv_path = os.path.join(OUTPUT_DIR, f"{prefix}_results.csv")
    if os.path.exists(csv_path):
        print(f"##vso[artifact.upload artifactname={prefix};]results/scan/{prefix}_results.csv")

def main():
    jobs = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(f"[CSV] Row: {row}")
            if row["project"] == SPECIFIC_PROJECT:
                print(f"[MATCH] Added: {row['repo']}")
                jobs.append((row["project"], row["repo"]))

    if not jobs:
        print(f"[INFO] No repositories found for project: {SPECIFIC_PROJECT}")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for job in jobs:
            executor.submit(clone_and_search, *job)

    print("\n[FINISHED] Check logs and results/ folder.")

if __name__ == "__main__":
    main()