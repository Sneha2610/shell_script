import os
import csv
import re
import tempfile
import subprocess
from pathlib import Path
import shutil

# === CONFIGURATION ===
ADO_ORG = "YOUR_ORG_NAME"  # 🔁 Replace with your Azure DevOps org name
ADO_PAT = os.getenv("ADO_PAT")
INPUT_CSV = "repo.csv"
OUTPUT_CSV = "report.csv"

if not ADO_PAT:
    raise EnvironmentError("Set your ADO_PAT environment variable.")

ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

# === FUNCTIONS ===

def build_repo_url(project, repo):
    return f"https://{ADO_ORG}@dev.azure.com/{ADO_ORG}/{project}/_git/{repo}"

def clone_repo(repo_url, clone_dir):
    auth_url = repo_url.replace("https://", f"https://:{ADO_PAT}@")
    print(f"🔄 Cloning: {repo_url}")
    result = subprocess.run(
        ["git", "clone", "--depth=1", auth_url, clone_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Clone failed: {repo_url}\n{result.stderr}")
        return False
    return True

def search_ips(project, repo, repo_path):
    results = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            path = Path(root) / file
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    ips = ip_regex.findall(content)
                    for ip in ips:
                        results.append({
                            "project": project,
                            "repo": repo,
                            "file": str(path.relative_to(repo_path)),
                            "ip": ip
                        })
            except Exception as e:
                print(f"⚠️ Failed to read {path}: {e}")
    return results

def write_results(results):
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline='') as csvfile:
        fieldnames = ["project", "repo", "file", "ip"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

# === MAIN SCRIPT ===

def main():
    with open(INPUT_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            project = row['project'].strip()
            repo = row['repo'].strip()
            repo_url = build_repo_url(project, repo)

            with tempfile.TemporaryDirectory() as tmpdir:
                repo_path = os.path.join(tmpdir, repo)
                if clone_repo(repo_url, repo_path):
                    ip_results = search_ips(project, repo, repo_path)
                    if ip_results:
                        write_results(ip_results)
                        print(f"✅ IPs found in {repo}. Logged to {OUTPUT_CSV}")
                    else:
                        print(f"✅ No IPs found in {repo}")
                # Repo is auto-deleted with TemporaryDirectory

    print("\n🚀 Scan complete.")

if __name__ == "__main__":
    main()
