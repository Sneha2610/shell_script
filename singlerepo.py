import os
import subprocess
import toml
import shutil
import pandas as pd

# Define the specific project and repository you want to test
project_name = 'your_project_name'  # Replace with your project name
repo_name = 'your_repo_name'        # Replace with your repository name

# Define paths and filenames
gitleaks_report_dir = 'gitleaks_reports'
rules_template = 'path/to/default/rules.toml'  # Template rules file
allowlist_repo_dir = '/path/to/checked_out_allowlist_repo'  # Path to the already checked out allowlist repo

# Paths to your Gitleaks binary and config file
gitleaks_binary = './tools/gitleaks'  # Adjust this path

# Create a directory to store the Gitleaks report if it doesn't exist
if not os.path.exists(gitleaks_report_dir):
    os.makedirs(gitleaks_report_dir)

# Personal Access Token for authentication
pat = os.environ['AZURE_DEVOPS_PAT']

# Construct the repository URL with PAT
repo_url = f"https://{pat}@dev.azure.com/your_organization/{project_name}/_git/{repo_name}"
clone_dir = os.path.join(gitleaks_report_dir, repo_name)

# Clone the repository
subprocess.run(['git', 'clone', repo_url, clone_dir])

# Locate the allowlist file in the checked-out allowlist repository
allowlist_path = os.path.join(allowlist_repo_dir, project_name, repo_name, 'allowlist.toml')

# Load the default rules template
with open(rules_template, 'r') as file:
    rules_data = toml.load(file)

# Merge allowlist into the rules file if the allowlist exists
if os.path.exists(allowlist_path):
    with open(allowlist_path, 'r') as allowlist_file:
        allowlist_data = toml.load(allowlist_file)
        # Assuming the allowlist is structured in a way that it can be directly merged
        rules_data['rules'].extend(allowlist_data.get('rules', []))

# Save the updated rules.toml to the cloned repository's directory
modified_rules_path = os.path.join(clone_dir, 'rules.toml')
with open(modified_rules_path, 'w') as modified_rules_file:
    toml.dump(rules_data, modified_rules_file)

# Run Gitleaks on the cloned repository using the modified rules
gitleaks_output = os.path.join(gitleaks_report_dir, f"{repo_name}_gitleaks.json")
subprocess.run([
    gitleaks_binary, 'detect', '--source', clone_dir,
    '--config-path', modified_rules_path,
    '--report-format', 'json', '--report-path', gitleaks_output
])

# If needed, read the report to verify its contents
report_df = pd.read_json(gitleaks_output)
print(report_df.head())  # Print the first few rows for verification

print(f"Gitleaks scan for {repo_name} completed. Report saved to {gitleaks_output}")
