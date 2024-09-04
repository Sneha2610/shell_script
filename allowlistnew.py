import os

ruleFilePath = 'gitleaks-config/rules.toml'
whitelistFilePath = 'gitleaks-config/secops/Gitleaks/gitleaks.toml'

# Function to read and extract lines after the description in file2
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
    with open(original_rule_file_path, 'r') as original_file:
        original_content = original_file.read()
    with open(rule_file_path, 'w') as rule_file:
        rule_file.write(original_content)

# Function to append lines to file1
def append_to_file(rule_file_path, lines):
    with open(rule_file_path, 'a') as f:
        f.write('\n')  # Ensure there's a newline before appending
        f.writelines(lines)

# Main logic
originalRuleFilePath = 'path/to/original/rules_template.toml'  # Path to the original rules template

if os.path.exists(whitelistFilePath):
    for repo in repos:  # Assuming `repos` is a list of repositories to iterate over
        # Reset the rule file to its original state before each iteration
        reset_rule_file(originalRuleFilePath, ruleFilePath)
        
        # Extract and append the whitelist data
        lines_after_description = extract_lines_after_description(whitelistFilePath)
        append_to_file(ruleFilePath, lines_after_description)
        
        # Run Gitleaks scan here for the current repository
        # subprocess.run([...])  # Add your Gitleaks command here
        
        # Optionally, you can remove the appended lines after the scan if necessary
else:
    print(f"{whitelistFilePath} does not exist.")
