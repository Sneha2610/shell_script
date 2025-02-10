import csv
import json
import os
import subprocess

# Configuration
CSV_FILE = "repositories.csv"  # Path to your input CSV file
GITLEAKS_BINARY = "./gitleaks"  # Path to Gitleaks binary
GITLEAKS_CONFIG = "./gitleaks_config.toml"  # Path to your custom Gitleaks rules file
OUTPUT_CSV = "gitleaks_consolidated_report.csv"  # Final consolidated report
BRANCHES = ["main", "release"]  # Branches to scan

# Ensure output directory exists
TEMP_REPO_DIR = "temp_repo"
os.makedirs(TEMP_REPO_DIR, exist_ok=True)

# Function to run Gitleaks with custom config
def run_gitleaks(project, repo, branch):
    repo_url = f"https://dev.azure.com/your-org/{project}/_git/{repo}"  # Modify as needed
    repo_dir = os.path.join(TEMP_REPO_DIR, repo)

    print(f"🔍 Scanning {repo} ({branch} branch) from {project}...")

    # Clone repository if not already cloned
    if os.path.exists(repo_dir):
        subprocess.run(["rm", "-rf", repo_dir], check=True)
    subprocess.run(["git", "clone", "--branch", branch, repo_url, repo_dir], check=True)

    # Run Gitleaks scan with custom config
    report_path = f"{repo}_{branch}.json"
    gitleaks_cmd = [
        GITLEAKS_BINARY, "detect", "--source", repo_dir, 
        "--config", GITLEAKS_CONFIG, 
        "--report-format", "json", "--report-path", report_path
    ]
    subprocess.run(gitleaks_cmd, check=True)

    # Parse Gitleaks JSON output
    findings = []
    if os.path.exists(report_path):
        with open(report_path, "r") as file:
            try:
                data = json.load(file)
                for item in data:
                    findings.append([
                        project, repo, branch, item.get("RuleID", "N/A"),
                        item.get("File", "N/A"), item.get("Commit", "N/A"),
                        item.get("StartLine", "N/A")
                    ])
            except json.JSONDecodeError:
                print(f"⚠️ Warning: No valid Gitleaks findings for {repo} ({branch})")

        # Remove temporary report JSON file
        os.remove(report_path)

    # Cleanup repository after scanning
    subprocess.run(["rm", "-rf", repo_dir], check=True)

    return findings

# Read repositories from CSV and scan them
all_findings = [["Project", "Repository", "Branch", "Secret Type", "File Path", "Commit ID", "Line Number"]]

with open(CSV_FILE, newline="") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    for row in reader:
        project, repo = row
        for branch in BRANCHES:
            all_findings.extend(run_gitleaks(project, repo, branch))

# Write findings to consolidated CSV
with open(OUTPUT_CSV, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(all_findings)

print(f"✅ Gitleaks scan completed! Consolidated report saved: {OUTPUT_CSV}")
