import csv
import os
import re
import subprocess
from tempfile import TemporaryDirectory

# === CONFIG ===
ORGANIZATION = "your-org-name"  # <-- Set your Azure DevOps organization name here
SEARCH_STRING = "your_search_string_here"  # <-- Set the string you want to search
INPUT_CSV = "repos.csv"
OUTPUT_CSV = "result.csv"
TOKEN = os.getenv("TOKEN")  # Set this as an environment variable before running

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

        for root, _, files in os.walk(temp_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if SEARCH_STRING in line:
                                rel_path = os.path.relpath(filepath
