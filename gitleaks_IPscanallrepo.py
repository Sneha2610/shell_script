import os
import subprocess
import json
import csv

# Environment variables
GITLEAKS_BINARY = "./gitleaks"  # Update if needed
GITLEAKS_CONFIG = "rules.toml"  # Custom Gitleaks config
GIT_PAT = os.getenv("TOKEN")  # PAT stored as an environment variable
INPUT_CSV = "projects_repos.csv"  # Input CSV with projects & repos
OUTPUT_CSV = "gitleaks_consolidated_report.csv"  # Final output CSV

# Function to scan repo branches
def scan_repo(project, repo):
    repo_url = f"https://oauth2:{GIT_PAT}@dev.azure.com/your-org/{project}/_git/{repo}"
    
    # Get all branches
    branches = get_branches(repo_url)

    # Filter branches (main + release/*)
    target_branches = ["main"] + [b for b in branches if b.startswith("release/")]

    for branch in target_branches:
        repo_dir = f"./{repo}_{branch.replace('/', '_')}"
        
        # Clone the repository (Handle branch errors)
        try:
            subprocess.run(
                ["git", "clone", "--branch", branch, repo_url, repo_dir],
                check=True
            )
        except subprocess.CalledProcessError:
            print(f"❌ Failed to clone {repo} ({branch})")
            continue  # Skip to the next branch

        # Run Gitleaks scan with custom config
        report_path = f"{repo}_{branch.replace('/', '_')}.json"
        gitleaks_cmd = [
            GITLEAKS_BINARY, "detect", "--source", repo_dir, 
            "--config", GITLEAKS_CONFIG, 
            "--report-format", "json", "--report-path", report_path
        ]
        
        result = subprocess.run(gitleaks_cmd, check=False)  # Allow failures
        
        if result.returncode != 0:
            print(f"⚠️ Leaks detected in {repo} ({branch}) - See {report_path}")
            parse_gitleaks_report(report_path, project, repo, branch)
        else:
            print(f"✅ No leaks found in {repo} ({branch})")

        # Cleanup repo after scan
        subprocess.run(["rm", "-rf", repo_dir], check=False)

# Function to get all branches of a repo
def get_branches(repo_url):
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url],
            capture_output=True, text=True, check=True
        )
        branches = [line.split("\t")[1].replace("refs/heads/", "") for line in result.stdout.splitlines()]
        return branches
    except subprocess.CalledProcessError:
        print(f"⚠️ Error fetching branches for {repo_url}")
        return []

# Function to parse Gitleaks JSON report and append to CSV
def parse_gitleaks_report(report_path, project, repo, branch):
    if not os.path.exists(report_path):
        return
    
    with open(report_path, "r") as file:
        try:
            leaks = json.load(file)
        except json.JSONDecodeError:
            print(f"⚠️ Error decoding JSON: {report_path}")
            return

    with open(OUTPUT_CSV, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        for leak in leaks:
            writer.writerow([
                project, repo, branch, 
                leak.get("RuleID", ""),
                leak.get("File", ""),
                leak.get("Match", ""),
                leak.get("StartLine", ""),  # Adding line number
                leak.get("Secret", ""),
                leak.get("Fingerprint", "")
            ])

# Initialize CSV with headers
with open(OUTPUT_CSV, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Project", "Repo", "Branch", "RuleID", "File", "Match", "Line Number", "Secret", "Fingerprint"])

# Read input CSV and scan all projects/repos
with open(INPUT_CSV, "r") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        project, repo = row
        scan_repo(project, repo)

print(f"✅ Consolidated report saved as {OUTPUT_CSV}")
