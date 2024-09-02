import os
import subprocess
import toml
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

# Assuming the source directory for scanning is already checked out or available locally
source_dir = f'/path/to/your/local/clone/of/{repo_name}'

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

# Save the updated rules.toml to the source directory
modified_rules_path = os.path.join(source_dir, 'rules.toml')
with open(modified_rules_path, 'w') as modified_rules_file:
    toml
