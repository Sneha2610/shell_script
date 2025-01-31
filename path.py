import os

# Paths for the rule file and whitelist file
ruleFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/rules-v8.toml')
whitelistFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/$(System.TeamProject)/$(Build.Repository.Name)/gitleaks.toml')

print(f"Rule File Path: {ruleFilePath}")
print(f"Whitelist File Path: {whitelistFilePath}")

# Function to read and extract lines after "description" in the whitelist file
def extract_lines_after_description(file_path):
    lines_to_append = []
    found_description = False
    print(f"Reading whitelist file: {file_path}")
    
    with open(file_path, 'r') as f:
        for line in f:
            if found_description:
                lines_to_append.append(line)
            elif line.strip().startswith("description"):
                found_description = True

    print("Extracted rules (regexes) from whitelist:", lines_to_append)
    return lines_to_append

# Function to append rules to the rules file
def append_to_rules_file(ruleFilePath, lines):
    if not lines:
        print("No new regex rules to append.")
        return
    
    with open(ruleFilePath, 'a') as f:
        f.write("\n")  # Ensure newline before appending
        f.writelines(lines)

    print("Rules appended successfully.")

# Function to extract paths from the whitelist file
def extract_paths_from_whitelist(file_path):
    paths = []
    in_allowlist_paths = False

    with open(file_path, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith("[allowlist.paths]"):
                in_allowlist_paths = True
                continue
            elif in_allowlist_paths:
                if stripped_line.startswith("["):  # New section starts
                    break
                paths.append(stripped_line)

    print("Extracted paths from whitelist:", paths)
    return paths

# Function to append paths to allowlist.paths section in rules file
def append_paths_to_rules_file(ruleFilePath, paths):
    if not paths:
        print("No new paths to append.")
        return

    updated_lines = []
    allowlist_paths_found = False
    allowlist_index = -1

    # Read the file and modify in memory
    with open(ruleFilePath, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        updated_lines.append(line)
        if line.strip().startswith("[allowlist.paths]"):
            allowlist_paths_found = True
            allowlist_index = i

    if allowlist_paths_found:
        # Append paths to existing [allowlist.paths] section
        updated_lines.insert(allowlist_index + 1, "\n".join(paths) + "\n")
    else:
        # Create the section if it doesn't exist
        updated_lines.append("\n[allowlist.paths]\n")
        updated_lines.append("\n".join(paths) + "\n")

    # Write updated content back
    with open(ruleFilePath, 'w') as f:
        f.writelines(updated_lines)

    print("Paths appended successfully.")

# Print file after modification
def print_file_content(file_path):
    print(f"\n--- Updated {file_path} ---\n")
    with open(file_path, 'r') as f:
        print(f.read())
    print("\n----------------------\n")

# Main execution
if os.path.exists(whitelistFilePath):
    print("Whitelist file exists. Processing...")

    # Extract and append regex rules
    lines_after_description = extract_lines_after_description(whitelistFilePath)
    append_to_rules_file(ruleFilePath, lines_after_description)

    # Extract and append paths
    paths = extract_paths_from_whitelist(whitelistFilePath)
    append_paths_to_rules_file(ruleFilePath, paths)

    # Print final file
    print_file_content(ruleFilePath)

else:
    print("Whitelist file does NOT exist. Exiting.")
