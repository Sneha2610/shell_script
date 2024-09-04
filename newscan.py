import os
import csv
import subprocess

# Paths to your rule file and original rule template
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

# Function to append lines to the rules file
def append_to_file(rule_file_path, lines):
    with open(rule_file_path, 'a') as f:
        f.write('\n')  # Ensure there's a newline before appending
        f.writelines(lines)

# Function to reset and rewrite the rules file
def reset_and_rewrite_rule_file(original_rule_file_path, rule_file_path):
    open(rule_file_path, 'w').close()  # Clears the content of the file
    shutil.copyfile(original_rule_file_path, rule_file_path)  # Rewrites with the original content
    print(f"Rules file has been reset and rewritten: {rule_file_path}")

# Main logic
input_csv = 'projects_and_repositories.csv'

with open(input_csv, 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        repo_name = row['repo_name']  # Correctly reference the 'repo_name' field in each row
        
        # Define paths specific to each repository
        whitelistFilePath = f'gitleaks-config/secops/Gitleaks/{repo_name}/gitleaks.toml'
        
        # Reset and rewrite the rules file to its original state before processing each repo
        reset_and_rewrite_rule_file(originalRuleFilePath, ruleFilePath)
        
        # Check if the whitelist file exists for the current repository
        if os.path.exists(whitelistFilePath):
            # Extract and append the whitelist data
            lines_after_description = extract_lines_after_description(whitelistFilePath)
            append_to_file(ruleFilePath, lines_after_description)
            
            # Print the appended lines (optional)
            print(f"Whitelist for {repo_name}:\n{''.join(lines_after_description)}")
        else:
            print(f"No whitelist found for {repo_name}, proceeding with default rules.")
        
        # Run Gitleaks scan (replace with your actual Gitleaks command)
        # subprocess.run([...])

print("All repositories processed. Gitleaks scans completed and rules file reset.")
