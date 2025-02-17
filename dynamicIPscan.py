trigger:
- none  # Change if needed

parameters:
  - name: rules_file
    displayName: "Select Rules File"
    type: string
    default: "rules1.toml"
    values:
      - "rules1.toml"
      - "rules2.toml"
      - "rules3.toml"

  - name: csv_file
    displayName: "Select Project CSV File"
    type: string
    default: "projects1_repos.csv"
    values:
      - "projects1_repos.csv"
      - "projects2_repos.csv"
      - "projects3_repos.csv"

jobs:
- job: GitleaksScan
  displayName: "Run Gitleaks Scan"
  pool:
    vmImage: ubuntu-latest

  steps:
  - checkout: self

  - script: |
      python scan_repos.py --rules ${{ parameters.rules_file }} --csv ${{ parameters.csv_file }}
    displayName: "Run Gitleaks with dynamic rules and projects"
