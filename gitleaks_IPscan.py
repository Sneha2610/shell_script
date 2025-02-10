import os
import subprocess

# Environment variables
GITLEAKS_BINARY = "./gitleaks"  # Update path if needed
GITLEAKS_CONFIG = "rules.toml"  # Custom Gitleaks config
GIT_PAT = os.getenv("TOKEN")  # Use environment variable for PAT

# Function to scan repo branches
def scan_repo(project, repo, branches):
    repo_url = f"https://oauth2:{GIT_PAT}@dev.azure.com/your-org/{project}/_git/{repo}"
    
    for branch in branches:
        repo_dir = f"./{repo}_{branch}"
        
        # Clone the repository (Handle branch errors)
        try:
            subprocess.run(
                ["git", "clone", "--branch", branch, repo_url, repo_dir],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone {repo} ({branch}): {e}")
            continue  # Skip to the next branch

        # Run Gitleaks scan with custom config
        report_path = f"{repo}_{branch}.json"
        gitleaks_cmd = [
            GITLEAKS_BINARY, "detect", "--source", repo_dir, 
            "--config", GITLEAKS_CONFIG, 
            "--report-format", "json", "--report-path", report_path
        ]
        
        result = subprocess.run(gitleaks_cmd, check=False)  # Allow failures
        
        if result.returncode == 0:
            print(f"✅ No leaks found in {repo} ({branch})")
        else:
            print(f"⚠️ Leaks detected in {repo} ({branch}) - See {report_path}")

        # Cleanup repo after scan
        subprocess.run(["rm", "-rf", repo_dir], check=False)

# Example usage
project = "MyProject"
repo = "MyRepo"
branches = ["main", "release"]

scan_repo(project, repo, branches)
