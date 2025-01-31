import os
import toml

# Define file paths
ruleFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/rules-v8.toml')
whitelistFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/$(System.TeamProject)/$(Build.Repository.Name)/gitleaks.toml')

print(f"Rule File Path: {ruleFilePath}")
print(f"Whitelist File Path: {whitelistFilePath}")

# Function to load a TOML file
def load_toml(file_path):
    try:
        with open(file_path, 'r') as f:
            return toml.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

# Function to update the allowlist in rules without affecting other rules
def merge_whitelist_to_rules(ruleFilePath, whitelistFilePath):
    # Load existing rules and whitelist
    rules = load_toml(ruleFilePath)
    whitelist = load_toml(whitelistFilePath)

    if "allowlist" not in whitelist:
        print("No allowlist found in whitelist file.")
        return
    
    # Extract paths and regexes from whitelist
    new_paths = set(whitelist["allowlist"].get("paths", []))
    new_regexes = set(whitelist["allowlist"].get("regexes", []))

    # Ensure allowlist exists in rules
    if "allowlist" not in rules:
        rules["allowlist"] = {}

    # Merge paths while avoiding duplicates
    existing_paths = set(rules["allowlist"].get("paths", []))
    merged_paths = list(existing_paths | new_paths)  # Union to avoid duplicates
    rules["allowlist"]["paths"] = merged_paths

    # Merge regexes while avoiding duplicates
    existing_regexes = set(rules["allowlist"].get("regexes", []))
    merged_regexes = list(existing_regexes | new_regexes)  # Union to avoid duplicates
    rules["allowlist"]["regexes"] = merged_regexes

    # Preserve other keys in allowlist (like regexesTarget)
    for key in rules["allowlist"]:
        if key not in ["paths", "regexes"]:
            rules["allowlist"][key] = rules["allowlist"][key]

    # Write back to the rules file
    with open(ruleFilePath, 'w') as f:
        toml.dump(rules, f)

    print("Rules file updated successfully.")

# Print final rules file content
def print_file_content(file_path):
    print(f"\n--- Updated {file_path} ---\n")
    with open(file_path, 'r') as f:
        print(f.read())
    print("\n----------------------\n")

# Main execution
if os.path.exists(whitelistFilePath):
    print("Whitelist file exists. Processing...")

    # Merge whitelist into rules
    merge_whitelist_to_rules(ruleFilePath, whitelistFilePath)

    # Print final rules file
    print_file_content(ruleFilePath)
else:
    print("Whitelist file does NOT exist. Exiting.")
