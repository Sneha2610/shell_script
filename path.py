import os
import toml

# Define file paths
ruleFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/rules-v8.toml')
whitelistFilePath = os.path.expandvars('$(System.DefaultWorkingDirectory)/gitleaks-config/$(System.TeamProject)/$(Build.Repository.Name)/gitleaks.toml')

# Load rules.toml
with open(ruleFilePath, 'r') as rule_file:
    rules_data = toml.load(rule_file)

# Load whitelist.toml
with open(whitelistFilePath, 'r') as whitelist_file:
    whitelist_data = toml.load(whitelist_file)

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
rules_data["allowlist"]["paths"] = merged_paths
rules_data["allowlist"]["regexes"] = merged_regexes

# Save updated rules.toml
with open(ruleFilePath, 'w') as updated_rule_file:
    toml.dump(rules_data, updated_rule_file)

print("rules-v8.toml updated successfully with merged allowlist.")
