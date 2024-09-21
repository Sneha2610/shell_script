# Define the base paths for Gitleaks and Whitelist repos
REPO_BASE_PATH="./repositories"
WHITELIST_BASE_PATH="./whitelist"
REPORTS_PATH="./reports"

# Create a reports directory if it doesn't exist
mkdir -p "$REPORTS_PATH"

# Read the CSV file and iterate over each repository
while IFS=',' read -r projectName repoName; do
  if [[ "$projectName" != "Project Name" ]]; then
    echo "Processing project: $projectName, repository: $repoName"

    # Clone the repository
    repoPath="$REPO_BASE_PATH/$repoName"
    if [ ! -d "$repoPath" ]; then
      git clone "https://your-git-server/$projectName/$repoName.git" "$repoPath"
    else
      echo "Repository $repoName already cloned."
    fi

    # Check if a whitelist (allowlist) file exists for the repository
    whitelistFile="$WHITELIST_BASE_PATH/$projectName/$repoName/gitleaks.toml"
    rulesFile="$repoPath/gitleaks-rules.toml"
    
    if [ -f "$whitelistFile" ]; then
      echo "Whitelist file found for $repoName."
      
      # Merge the whitelist with the Gitleaks rules inline
      echo "Merging whitelist with rules.toml"
      cat "$whitelistFile" >> "$rulesFile"
      
      # Run Gitleaks scan with the merged rules
      echo "Running Gitleaks scan with updated rules for $repoName"
      cd "$repoPath"
      ./gitleaks --config "$rulesFile" --path . --report-format csv --report-path "$REPORTS_PATH/${repoName}-gitleaks-report.csv"
      
    else
      echo "No whitelist file found for $repoName. Using default rules."
      
      # Run Gitleaks scan with default rules
      cd "$repoPath"
      ./gitleaks --config "$rulesFile" --path . --report-format csv --report-path "$REPORTS_PATH/${repoName}-gitleaks-report.csv"
    fi
    
    # Go back to the base directory after the scan
    cd - 
    echo "Completed Gitleaks scan for $repoName. Report saved to $REPORTS_PATH/${repoName}-gitleaks-report.csv"
  fi
done < $(Build.SourcesDirectory)/project_and_repositories.csv
