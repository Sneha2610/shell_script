import os

# Paths for the rule file and whitelist file
ruleFilePath = '$(System.DefaultWorkingDirectory)/gitleaks-config/rules-v8.toml'
whitelistFilePath = '$(System.DefaultWorkingDirectory)/gitleaks-config/$(System.TeamProject)/$(Build.Repository.Name)/gitleaks.toml'

# Function to read and extract lines after the "description" in the whitelist file
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

# Function to append regexes or other rules to the rules file
def append_to_rules_file(ruleFilePath, lines):
    with open(ruleFilePath, 'a') as f:
        f.write("\n")  # Ensure there's a newline before appending
        f.writelines(lines)

# Function to extract paths from the whitelist file
def extract_paths_from_whitelist(file_path):
    paths = []
    in_allowlist_paths = False
    with open(file_path, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith("[allowlist.paths]"):
                in_allowlist_paths = True
            elif in_allowlist_paths:
                if stripped_line.startswith("["):  # End of allowlist.paths section
                    break
                paths.append(stripped_line)
    return paths

# Function to append paths to the allowlist.paths section in the rules file
def append_paths_to_rules_file(ruleFilePath, paths):
    updated_lines = []
    allowlist_paths_found = False

    with open(ruleFilePath, 'r') as f:
        for line in f:
            updated_lines.append(line)
            if line.strip().startswith("[allowlist.paths]"):
                allowlist_paths_found = True

    # If the allowlist.paths section is found, append the new paths
    if allowlist_paths_found:
        updated_lines.append("\n".join(paths) + "\n")
    else:
        # If allowlist.paths section is not found, create it
        updated_lines.append("\n[allowlist.paths]\n")
        updated_lines.append("\n".join(paths) + "\n")

    # Write the updated lines back to the rules file
    with open(ruleFilePath, 'w') as f:
        f.writelines(updated_lines)

    # Print the contents of the file after appending
    print("\nUpdated rules file content:\n")
    with open(ruleFilePath, 'r') as f:
        print(f.read())

# Main logic
if os.path.exists(whitelistFilePath):
    # Extract lines after the "description"
    lines_after_description = extract_lines_after_description(whitelistFilePath)
    append_to_rules_file(ruleFilePath, lines_after_description)

    # Extract paths and append to allowlist.paths
    paths = extract_paths_from_whitelist(whitelistFilePath)
    if paths:
        append_paths_to_rules_file(ruleFilePath, paths)
else:
    print("Whitelist file does not exist")
