import os
import csv
import tempfile
import shutil
import re
from git import Repo
from concurrent.futures import ThreadPoolExecutor
import threading

# === CONFIG ===
ADO_ORG = "your-org"  # <-- Replace with your ADO organization name
SEARCH_STRING = "your_search_string"  # <-- Replace with the keyword you're searching for
SPECIFIC_PROJECT = "YourSpecificProject"  # <-- Replace with the specific project you want to scan
INPUT_CSV = "repos.csv"
OUTPUT_DIR = "results"
THREADS = 5

# === AUTH ===
PAT = os.getenv("ADO_PAT")
if not PAT:
    raise Exception("ADO_PAT environment variable is not set.")

# === SHARED STATE ===
found_prefixes = set()
lock = threading.Lock()


def get_repo_prefix(repo_name):
    match = re.match(r'^([a-zA-Z0-9]+)[-_\.]?', repo_name)
    return match.group(1) if match else repo_name[:7]


def get_default_branch(repo_path):
    try:
        return Repo(repo_path).active_branch.name
    except:
        head_ref = Repo(repo_path).git.symbolic_ref("HEAD")
        return head_ref.split("/")[-1]


def clone_and_search(project, repo_name):
    prefix = get_repo_prefix(repo_name)

    with lock:
        if prefix in found_prefixes:
            print(f"[SKIPPED] {repo_name} (prefix {prefix} already found)")
            return

    remote_url = f"https://{PAT}@dev.azure.com/{ADO_ORG}/{project}/_git/{repo_name}"
    workdir = tempfile.mkdtemp()

    try:
        print(f"[CLONING] {project}/{repo_name}")
        repo_path = os.path.join(workdir, repo_name)
        repo = Repo.clone_from(remote_url, repo_path)

        branch = get_default_branch(repo_path)
        if not branch.startswith("release"):
            print(f"  [SKIPPED] {repo_name} (non-release branch: {branch})")
            return

        repo.git.checkout(branch)

        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if SEARCH_STRING in line:
                                rel_path = os.path.relpath(file_path, repo_path)
                                row = [project, repo_name, rel_path, branch, i]
                                print(f"    [FOUND] {rel_path}:{i}")
                                write_result(prefix, row)
                                publish_artifact(prefix)
                                with lock:
                                    found_prefixes.add(prefix)
                                return
                except Exception as e:
                    print(f"    [ERROR] reading {file_path}: {e}")

        print(f"  [NO MATCH] {project}/{repo_name}")

    except Exception as e:
        print(f"[ERROR] {project}/{repo_name}: {e}")
    finally:
        shutil.rmtree(workdir)


def write_result(prefix, row):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, f"{prefix}_results.csv")
    write_header = not os.path.exists(csv_path)

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Project", "Repo", "File Path", "Branch", "Line Number"])
        writer.writerow(row)


def publish_artifact(prefix):
    csv_path = os.path.join(OUTPUT_DIR, f"{prefix}_results.csv")
    if os.path.exists(csv_path):
        print(f"##vso[artifact.upload artifactname={prefix};]results/{prefix}_results.csv")


def main():
    jobs = []

    with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["project"] == SPECIFIC_PROJECT:
                jobs.append((row["project"], row["repo"]))

    if not jobs:
        print(f"[INFO] No repositories found for project: {SPECIFIC_PROJECT}")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for job in jobs:
            executor.submit(clone_and_search, *job)

    print(f"\n[FINISHED] Search completed for project: {SPECIFIC_PROJECT}. Check logs and ADO artifacts per prefix.")


if __name__ == "__main__":
    main()