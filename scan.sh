#!/bin/bash

# Paths to directories and files
ALLOWLIST_REPO_DIR="path/to/checked_out_allowlist_repo"
GITLEAKS_BINARY="./path/to/gitleaks"  # Update this to the actual path of your Gitleaks binary in the repo
RULES_TEMPLATE="path/to/default/rules.toml"
GITLEAKS_REPORT_DIR="gitleaks_reports"
CSV_FILE="repos_list.csv"
COMBINED_CSV_REPORT="combined_gitleaks_report.csv"

# Make sure the Gitleaks binary is executable
chmod +x "$GITLEAKS_BINARY"

# Create a directory to store the Gitleaks reports if it doesn't exist
mkdir -p "$GITLEAKS_REPORT_DIR"

# Initialize the combined CSV file with headers
echo "Repo,RuleID,Description,File,Commit,Line,Author,Date,Message" > "$COMBINED_CSV_REPORT"

# Iterate over each line in the CSV file
while IFS=, read -r project_name repo_name; do
    echo "Processing project: $project_name, repo: $repo_name"

    # Define paths
    allowlist_path="$ALLOWLIST_REPO_DIR/$project_name/$repo_name/allowlist.toml"
    source_dir="/path/to/your/local/clone/of/$repo_name"
    modified_rules_path="$source_dir/rules.toml"

    # Check if the allowlist file exists
    if [ -f "$allowlist_path" ]; then
        echo "Allowlist found for $repo_name. Merging with rules.toml."

        # Run the Python script to merge the allowlist with rules.toml
        python3 <<EOF
import toml
import os

# Load the default rules template
rules_template = "$RULES_TEMPLATE"
with open(rules_template, 'r') as file:
    rules_data = toml.load(file)

# Merge the allowlist with the rules.toml
allowlist_path = "$allowlist_path"
with open(allowlist_path, 'r') as allowlist_file:
    allowlist_data = toml.load(allowlist_file)
    rules_data['rules'].extend(allowlist_data.get('rules', []))

# Save the merged rules.toml
modified_rules_path = "$modified_rules_path"
with open(modified_rules_path, 'w') as modified_rules_file:
    toml.dump(rules_data, modified_rules_file)

EOF
    else
        echo "No allowlist found for $repo_name. Using default rules.toml."
        cp "$RULES_TEMPLATE" "$modified_rules_path"
    fi

    # Run Gitleaks in no-git mode
    gitleaks_output="$GITLEAKS_REPORT_DIR/${repo_name}_gitleaks.json"
    "$GITLEAKS_BINARY" detect --no-git --source "$source_dir" \
        --config-path "$modified_rules_path" \
        --report-format json --report-path "$gitleaks_output"

    echo "Gitleaks scan for $repo_name completed. Report saved to $gitleaks_output"

    # Convert the JSON report to CSV format and append to the combined CSV report
    jq -r --arg repo "$repo_name" '.[] | [$repo, .ruleID, .description, .file, .commit, .line, .author, .date, .message] | @csv' "$gitleaks_output" >> "$COMBINED_CSV_REPORT"

done < "$CSV_FILE"

echo "Combined CSV report generated at $COMBINED_CSV_REPORT"
