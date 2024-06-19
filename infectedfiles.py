trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- script: |
    sudo apt-get update
    sudo apt-get install -y clamav
    clamscan -r . > clamav.log
  displayName: 'Run ClamAV Scan'

- script: |
    python extract_and_generate_report.py
  displayName: 'Generate HTML Report'
  
- task: PublishBuildArtifacts@1
  inputs:
    pathtoPublish: 'clamav_report.html'
    artifactName: 'ClamAVReport'
  displayName: 'Publish HTML Report'
