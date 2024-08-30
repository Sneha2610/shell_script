import os
import csv
import subprocess
import pandas as pd

# Define paths and filenames
input_csv = 'projects_and_repositories.csv'
output_csv = 'gitleaks_report.csv'
gitleaks_report_dir = 'gitleaks_reports'

# Paths to your Gitleaks binary and config file
gitleaks_binary = 'path/to/gitleaks'  # Adjust this path
gitleaks_config = 'path/to/gitleaks.toml'  # Adjust this path

# Create a directory to store individual Gitleaks reports
if not os.path.exists(gitleaks_report_dir):
    os.makedirs(gitleaks_report_dir)

# Read the CSV file
with open(input_csv, 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        project_name = row['Project Name']
        repo_name = row['Repository Name']

        # Clone the repository (assuming you have access to the repo URL)
        repo_url = f"https://dev.azure.com/your_organization/{project_name}/_git/{repo_name}"
        clone_dir = os.path.join(gitleaks_report_dir, repo_name)
        subprocess.run(['git', 'clone', repo_url, clone_dir])

        # Run Gitleaks on the cloned repository using your binary and config
        gitleaks_output = os.path.join(gitleaks_report_dir, f"{repo_name}_gitleaks.json")
        subprocess.run([
            gitleaks_binary, 'detect', '--source', clone_dir,
            '--config-path', gitleaks_config,
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
