import os

# Define file paths
ruleFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/rules-v8.toml')
whitelistFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/$(System.TeamProject)/$(Build.Repository.Name)/gitleaks.toml')

print(f"Rule File Path: {ruleFilePath}")
print(f"Whitelist File Path: {whitelistFilePath}")

# Function to extract allowlist paths from the whitelist file
def extract_paths_from_whitelist(file_path):
    paths = []
    in_allowlist_paths = False

    with open(file_path, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith("[allowlist.paths]"):
                in_allowlist_paths = True
                continue  # Skip the section header
            elif in_allowlist_paths:
                if stripped_line.startswith("["):  # New section starts, stop reading
                    break
                paths.append(stripped_line)  # Collect paths

    print("Extracted paths from whitelist:", paths)
    return paths

# Function to append new paths to [allowlist.paths] in rules file
def append_paths_to_rules_file(ruleFilePath, new_paths):
    if not new_paths:
        print("No new paths to append.")
        return

    updated_lines = []
    allowlist_paths_found = False
    existing_paths = set()
    allowlist_index = -1

    # Read the file and track existing allowlist paths
    with open(ruleFilePath, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        updated_lines.append(line)
        if line.strip().startswith("[allowlist.paths]"):
            allowlist_paths_found = True
            allowlist_index = i
        elif allowlist_paths_found and line.strip():  # If inside allowlist.paths
            if line.strip().startswith("["):  # Stop if a new section starts
                break
            existing_paths.add(line.strip())

    # Filter out already existing paths
    paths_to_add = [path for path in new_paths if path not in existing_paths]

    if paths_to_add:
        if allowlist_paths_found:
            updated_lines.insert(allowlist_index + 1, "\n".join(paths_to_add) + "\n")
        else:
            updated_lines.append("\n[allowlist.paths]\n")
            updated_lines.append("\n".join(paths_to_add) + "\n")

        # Write updated content back
        with open(ruleFilePath, 'w') as f:
            f.writelines(updated_lines)

        print("Paths appended successfully.")
    else:
        print("All whitelist paths already exist in rules file. No changes made.")

# Print final rules file content
def print_file_content(file_path):
    print(f"\n--- Updated {file_path} ---\n")
    with open(file_path, 'r') as f:
        print(f.read())
    print("\n----------------------\n")

# Main execution
if os.path.exists(whitelistFilePath):
    print("Whitelist file exists. Processing...")

    # Extract and append paths
    paths = extract_paths_from_whitelist(whitelistFilePath)
    append_paths_to_rules_file(ruleFilePath, paths)

    # Print final file
    print_file_content(ruleFilePath)
else:
    print("Whitelist file does NOT exist. Exiting.")
