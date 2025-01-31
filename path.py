import os
import toml

# Define file paths
ruleFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/rules-v8.toml')
whitelistFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/$(System.TeamProject)/$(Build.Repository.Name)/gitleaks.toml')

def load_toml(file_path):
    """Load TOML file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return toml.load(f)
    except toml.TomlDecodeError as e:
        print(f"TOML Decode Error in {file_path}: {e}")
        exit(1)

# Load TOML files
rules_data = load_toml(ruleFilePath)
whitelist_data = load_toml(whitelistFilePath)

# Extract allowlist sections
rules_allowlist = rules_data.get("allowlist", {})
whitelist_allowlist = whitelist_data.get("allowlist", {})

# Merge paths
existing_paths = set(rules_allowlist.get("paths", []))
new_paths = set(whitelist_allowlist.get("paths", []))
merged_paths = list(existing_paths | new_paths)

# Merge regexes
existing_regexes = set(rules_allowlist.get("regexes", []))
new_regexes = set(whitelist_allowlist.get("regexes", []))
merged_regexes = list(existing_regexes | new_regexes)

# Update rules with merged allowlist
rules_data.setdefault("allowlist", {})["paths"] = merged_paths
rules_data.setdefault("allowlist", {})["regexes"] = merged_regexes

# Save updated rules.toml
with open(ruleFilePath, 'w', encoding='utf-8') as updated_rule_file:
    toml.dump(rules_data, updated_rule_file)

print("rules-v8.toml updated successfully with merged allowlist.")
