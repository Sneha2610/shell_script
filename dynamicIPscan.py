import os
import subprocess
import json
import csv
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run Gitleaks scan with dynamic rules and multiple CSV files")
parser.add_argument("--rules", required=True, help="Path to rules.toml file")
parser.add_argument("--csv", required=True, help="Comma-separated CSV file paths")
args = parser.parse_args()

# Convert CSV argument to a list
csv_files = args.csv.split(",")

# Environment variables
GITLEAKS_BINARY = "./gitleaks"  # Update if needed
GIT_PAT = os.getenv("TOKEN")  # PAT stored as an environment variable
OUTPUT_CSV = "gitleaks_consolidated_report.csv"  # Final output CSV

# Function to scan repo branches
def scan_repo(project, repo, rules_file):
    repo_url = f"https://oauth2:{GIT_PAT}@dev.azure.com/your-org/{project}/_git/{repo}"
    
    # Get all branches
    branches = get_branches(repo_url)

    # Filter branches (main + release/*)
    target_branches = ["main"] + [b for b in branches if b.startswith("release/")]

    for branch in target_branches:
        repo_dir = f"./{repo}_{branch.replace('/', '_')}"
        
        # Clone the repository
        try:
            subprocess.run(["git", "clone", "--branch", branch, repo_url, repo_dir], check=True)
        except subprocess.CalledProcessError:
            print(f"❌ Failed to clone {repo} ({branch})")
            continue

        # Run Gitleaks scan
        report_path = f"{repo}_{branch.replace('/', '_')}.json"
        gitleaks_cmd = [
            GITLEAKS_BINARY, "detect", "--source", repo_dir, 
            "--config", rules_file, 
            "--report-format", "json", "--report-path", report_path
        ]
        
        result = subprocess.run(gitleaks_cmd, check=False)
        
        if result.returncode != 0:
            print(f"⚠️ Leaks detected in {repo} ({branch}) - See {report_path}")
            parse_gitleaks_report(report_path, project, repo, branch)
        else:
            print(f"✅ No leaks found in {repo} ({branch})")

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
                leak.get("StartLine", ""),  
                leak.get("Secret", ""),
                leak.get("Fingerprint", "")
            ])

# Initialize CSV with headers
with open(OUTPUT_CSV, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Project", "Repo", "Branch", "RuleID", "File", "Match", "Line Number", "Secret", "Fingerprint"])

# Process each CSV file
for csv_file in csv_files:
    if not os.path.exists(csv_file):
        print(f"⚠️ CSV file not found: {csv_file}")
        continue

    with open(csv_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            project, repo = row
            scan_repo(project, repo, args.rules)

print(f"✅ Consolidated report saved as {OUTPUT_CSV}")
