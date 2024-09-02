import os
import csv
import subprocess
import toml
import shutil
import pandas as pd

# Define paths and filenames
input_csv = 'projects_and_repositories.csv'
output_csv = 'gitleaks_report.csv'
gitleaks_report_dir = 'gitleaks_reports'
rules_template = 'path/to/default/rules.toml'  # Template rules file
allowlist_repo_dir = '/path/to/checked_out_allowlist_repo'  # Path to the already checked out allowlist repo

# Paths to your Gitleaks binary and config file
gitleaks_binary = './tools/gitleaks'  # Adjust this path

# Create a directory to store individual Gitleaks reports
if not os.path.exists(gitleaks_report_dir):
    os.makedirs(gitleaks_report_dir)

# Personal Access Token for authentication
pat = os.environ['AZURE_DEVOPS_PAT']

# Read the CSV file
with open(input_csv, 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        project_name = row['Project Name']
        repo_name = row['Repository Name']

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

# Combine all JSON reports into a single CSV file
reports = []
for report_file in os.listdir(gitleaks_report_dir):
    if report_file.endswith('_gitleaks.json'):
        report_path = os.path.join(gitleaks_report_dir, report_file)
        repo_df = pd.read_json(report_path)
        reports.append(repo_df)

# Concatenate all reports into a single DataFrame
final_report = pd.concat(reports, ignore_index=True)
# Write the final report to CSV
final_report.to_csv(output_csv, index=False)

print(f"Gitleaks scan completed. Consolidated report saved to {output_csv}")
