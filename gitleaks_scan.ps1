param (
    [string]$projectName,
    [string]$repoName
)

# Navigate to the repository directory and run Gitleaks
cd $repoName
./gitleaks --config ./gitleaks.toml --path . --report-path ./gitleaks-report.json

# Generate HTML report from JSON if needed
python generate_html_report.py ./gitleaks-report.json ./gitleaks-report.html

cd ..
