import csv
import os
import subprocess

# Define paths
repo_base_path = "./repositories"  # Directory where repositories will be cloned
whitelist_base_path = "./whitelist"  # Directory where whitelist files are stored
reports_path = "./reports"  # Directory to save reports
gitleaks_binary = "/path/to/gitleaks"  # Path to your Gitleaks binary
default_rules_file = "/path/to/default/gitleaks-rules.toml"  # Path to your default Gitleaks rules file

# Create reports directory if it doesn't exist
os.makedirs(reports_path, exist_ok=True)

# Function to run a command and capture output
def run_command(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
    return result

# Read the CSV file and iterate over each project and repository
csv_file_path = os.path.join(os.getenv("Build_SourcesDirectory"), "project_and_repositories.csv")
with open(csv_file_path, mode='r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip header

    for row in csv_reader:
        project_name, repo_name = row
        print(f"Processing project: {project_name}, repository: {repo_name}")

        # Clone the repository
        repo_path = os.path.join(repo_base_path, repo_name)
        if not os.path.isdir(repo_path):
            clone_command = f"git clone https://your-git-server/{project_name}/{repo_name}.git {repo_path}"
            run_command(clone_command)
        else:
            print(f"Repository {repo_name} already cloned.")

        # Check if a whitelist file exists for the repository
        whitelist_file = os.path.join(whitelist_base_path, project_name, repo_name, "gitleaks.toml")
        rules_file = os.path.join(repo_path, "gitleaks-rules.toml")
        
        if os.path.isfile(whitelist_file):
            print(f"Whitelist file found for {repo_name}. Merging with rules.toml.")
            
            # Copy default rules to the repository directory and append whitelist
            shutil.copy(default_rules_file, rules_file)
            with open(rules_file, 'a') as rules, open(whitelist_file, 'r') as whitelist:
                rules.write(whitelist.read())
        else:
            print(f"No whitelist file found for {repo_name}. Using default rules.")
            # Use default rules if no whitelist exists
            shutil.copy(default_rules_file, rules_file)

        # Run Gitleaks scan with the appropriate rules file and save report as CSV
        report_file = os.path.join(reports_path, f"{repo_name}-gitleaks-report.csv")
        gitleaks_command = f"{gitleaks_binary} --config {rules_file} --path {repo_path} --report-format csv --report-path {report_file}"
        run_command(gitleaks_command)

        print(f"Completed Gitleaks scan for {repo_name}. Report saved to {report_file}")

print("All scans completed.")
