import os
import csv
import subprocess
import shutil

# Paths to your rule file and whitelist file
ruleFilePath = 'gitleaks-config/rules.toml'
originalRuleFilePath = 'path/to/original/rules_template.toml'  # Path to the original rules template

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

# Function to reset the rule file to its original state
def reset_rule_file(original_rule_file_path, rule_file_path):
    shutil.copyfile(original_rule_file_path, rule_file_path)

# Function to append lines to the rules file
def append_to_file(rule_file_path, lines):
    with open(rule_file_path, 'a') as f:
        f.write('\n')  # Ensure there's a newline before appending
        f.writelines(lines)

# CSV file containing repository names
input_csv = 'projects_and_repositories.csv'

# Personal Access Token for authentication
pat = os.environ['AZURE_DEVOPS_PAT']

# Create a directory to store individual Gitleaks reports
gitleaks_report_dir = 'gitleaks_reports'
if not os.path.exists(gitleaks_report_dir):
    os.makedirs(gitleaks_report_dir)

# Main logic
with open(input_csv, 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        repo_name = row['repo_name']  # Correctly reference the 'repo_name' field in each row
        
        # Define paths specific to each repository
        whitelistFilePath = f'gitleaks-config/secops/Gitleaks/{repo_name}/gitleaks.toml'
        
        # Reset the rule file to its original state before each iteration
        reset_rule_file(originalRuleFilePath, ruleFilePath)
        
        # Check if the whitelist file exists for the current repository
        if os.path.exists(whitelistFilePath):
            # Extract and append the whitelist data
            lines_after_description = extract_lines_after_description(whitelistFilePath)
            append_to_file(ruleFilePath, lines_after_description)
            
            # Print the appended lines (optional)
            print(f"Whitelist for {repo_name}:\n{''.join(lines_after_description)}")
        else:
            print(f"No whitelist found for {repo_name}, proceeding with default rules.")
        
        # Define paths for cloning and output
        clone_dir = os.path.join(gitleaks_report_dir, repo_name)
        repo_url = f"https://{pat}@dev.azure.com/your_organization/_git/{repo_name}"
        gitleaks_output = os.path.join(clone_dir, f"{repo_name}_gitleaks.json")
        
        # Clone the repository
        subprocess.run(['git', 'clone', repo_url, clone_dir])
        
        # Run Gitleaks in no-git mode on the cloned repository using the modified rules
        subprocess.run([
            './tools/gitleaks', 'detect', '--no-git', '--source', clone_dir,
            '--config-path', ruleFilePath,
            '--report-format', 'json', '--report-path', gitleaks_output
        ])
        
        # Optionally, print a message after each scan
        print(f"Completed Gitleaks scan for {repo_name}. Report saved to {gitleaks_output}")

print("All repositories processed. Gitleaks scans completed.")
