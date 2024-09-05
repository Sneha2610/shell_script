import os
import csv
import subprocess
import shutil
import pandas as pd

# Define paths
input_csv = 'projects_and_repositories.csv'
output_csv = 'gitleaks_report.csv'
gitleaks_report_dir = 'gitleaks_reports'
rules_template = 'path/to/rules.toml'  # Template rules file
whitelist_repo_dir = '/path/to/checked_out_allowlist_repo'  # Whitelist repo directory
gitleaks_binary = './tools/gitleaks'  # Gitleaks binary path

# Create a directory to store individual Gitleaks reports
if not os.path.exists(gitleaks_report_dir):
    os.makedirs(gitleaks_report_dir)

# Function to read and extract lines after the description in the whitelist file
def extract_lines_after_description(file_path):
    lines_to_append = []
    found_description = False
    with open(file_path, 'r') as f:
        for line in f:
            if found_description:
                lines_to_append.append(line)
            elif line.strip().startswith("description"):
                found_description = True
    return lines_to_append

# Function to append lines to the rules file
def append_to_file(rules_file_path, lines):
    with open(rules_file_path, 'a') as f:
        f.write('\n')  # Ensure there's a newline before appending
        f.writelines(lines)

# Function to rename the rules file for each repo
def rename_rules_file(rules_template_path, repo_name):
    renamed_rules_path = f'gitleaks-config/{repo_name}_rules.toml'
    shutil.copyfile(rules_template_path, renamed_rules_path)
    print(f"Renamed rules file to: {renamed_rules_path}")
    return renamed_rules_path

# Main logic
repos_scanned = []

with open(input_csv, 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        project_name = row['project_name']
        repo_name = row['repo_name']

        # Define repository URL and local paths
        repo_url = f"https://{os.getenv('AZURE_DEVOPS_PAT')}@dev.azure.com/your_organization/{project_name}/_git/{repo_name}"
        clone_dir = os.path.join(gitleaks_report_dir, repo_name)
        whitelist_file_path = os.path.join(whitelist_repo_dir, project_name, repo_name, 'gitleaks.toml')
        gitleaks_output = os.path.join(gitleaks_report_dir, f"{repo_name}_gitleaks.json")
        
        # Step 1: Clone the repository
        subprocess.run(['git', 'clone', repo_url, clone_dir])

        # Step 2: Rename the rules file for this repo
        repo_rules_file = rename_rules_file(rules_template, repo_name)

        # Step 3: Check for whitelist and append if exists
        if os.path.exists(whitelist_file_path):
            lines_after_description = extract_lines_after_description(whitelist_file_path)
            append_to_file(repo_rules_file, lines_after_description)
            print(f"Whitelist appended for {project_name}/{repo_name}")
        else:
            print(f"No whitelist found for {project_name}/{repo_name}, using default rules.")

        # Step 4: Run Gitleaks with the renamed rules file
        subprocess.run([
            gitleaks_binary, 'detect', '--no-git', '--source', clone_dir,
            '--config-path', repo_rules_file,
            '--report-format', 'json', '--report-path', gitleaks_output
        ])
        
        # Record the repo scanned
        repos_scanned.append(gitleaks_output)

# Step 5: Combine all JSON reports into a single CSV
reports = []
for report_file in repos_scanned:
    repo_df = pd.read_json(report_file)
    reports.append(repo_df)

# Concatenate all reports into a single DataFrame
final_report = pd.concat(reports, ignore_index=True)

# Write the final report to a CSV file
final_report.to_csv(output_csv, index=False)

print(f"Gitleaks scan completed. Consolidated report saved to {output_csv}")
