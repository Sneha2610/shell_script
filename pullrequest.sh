steps:
  - script: |
      if [ "$(Build.Reason)" = "PullRequest" ]; then
        echo "Pull Request Commit ID: $(System.PullRequest.SourceCommitId)"
      else
        echo "This is not a pull request build."
      fi
    displayName: 'Print Source Commit ID in PR builds'
