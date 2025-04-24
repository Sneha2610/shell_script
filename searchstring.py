import os
import csv
import tempfile
import shutil
import fnmatch
import subprocess
from git import Repo
from concurrent.futures import ThreadPoolExecutor

# === CONFIG ===
ADO_ORG = "your-org-name"  # <-- Replace this
ADO_URL = f"https://dev.azure.com/{ADO_ORG}"
SEARCH_STRING = "your_search_string"  # <-- Replace this
CSV_FILE = "release_search_results.csv"
INPUT_CSV = "repos.csv"
THREADS = 5

# === AUTH ===
PAT = os.getenv("ADO_PAT")
if not PAT:
    raise Exception("ADO_PAT environment variable not set")


def clone_and_search(project, repo_name):
    print(f"[START] {project}/{repo_name}")
    remote_url = f"https://{PAT}@dev.azure.com/{ADO_ORG}/{project}/_git/{repo_name}"
    workdir = tempfile.mkdtemp()

    try:
        repo_path = os.path.join(workdir, repo_name)
        bare_repo = Repo.clone_from(remote_url, repo_path, multi_options=["--mirror"])

        # Find all release/* branches
        refs = subprocess.check_output(
            ["git", "--git-dir", repo_path, "for-each-ref", "--format=%(refname:short)"],
            text=True
        )
        branches = [ref for ref in refs.splitlines() if fnmatch.fnmatch(ref, "release/*")]

        for branch in branches:
            print(f"[BRANCH] {repo_name}: {branch}")
            branch_dir = os.path.join(workdir, f"{repo_name}_{branch.replace('/', '_')}")
            Repo.clone_from(remote_url, branch_dir, branch=branch, depth=1)

            for root, _, files in os.walk(branch_dir):
                for file in files:
                    try:
                        full_path = os.path.join(root, file)
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if SEARCH_STRING in line:
                                    rel_path = os.path.relpath(full_path, branch_dir)
                                    row = [SEARCH_STRING, project, repo_name, branch, rel_path, i]
                                    print("FOUND:", row)
                                    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as out:
                                        csv.writer(out).writerow(row)
                    except Exception as e:
                        print(f"[ERROR] Failed reading file {file}: {e}")
    except Exception as e:
        print(f"[ERROR] {project}/{repo_name}: {e}")
    finally:
        shutil.rmtree(workdir)


def main():
    # Write CSV headers
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as out:
        csv.writer(out).writerow(["Search String", "Project", "Repo", "Branch", "File Path", "Line Number"])

    jobs = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            jobs.append((row["project"], row["repo"]))

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for job in jobs:
            executor.submit(clone_and_search, *job)


if __name__ == "__main__":
    main()