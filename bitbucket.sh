#!/bin/bash

# Bitbucket API credentials
username='your_username'
password='your_password'

# Path to the text file containing random words
file_path='path/to/text_file.txt'

# Read the random words from the file
random_words=$(cat "$file_path")

# Bitbucket REST API endpoint for searching projects
projects_url="https://api.bitbucket.org/2.0/workspaces"

# Perform the search for each random word
for word in $random_words; do
  echo "Searching for word: $word"
  echo

  # Search for projects
  projects_response=$(curl -s -u "$username:$password" "$projects_url?q=$word")

  # Process projects search response
  projects_size=$(echo "$projects_response" | jq -r '.size')
  if [[ "$projects_size" -gt 0 ]]; then
    echo "Projects containing the word '$word':"
    echo "$projects_response" | jq -r '.values[].name'
    echo
  else
    echo "No projects found containing the word '$word'."
    echo
  fi

  # Iterate through projects and search for repositories
  projects=$(echo "$projects_response" | jq -r '.values[].key')
  for project in $projects; do
    repositories_url="https://api.bitbucket.org/2.0/repositories/$project"

    # Search for repositories in the project
    repositories_response=$(curl -s -u "$username:$password" "$repositories_url?q=$word")

    # Process repositories search response
    repositories_size=$(echo "$repositories_response" | jq -r '.size')
    if [[ "$repositories_size" -gt 0 ]]; then
      echo "Repositories containing the word '$word' in the project '$project':"
      echo "$repositories_response" | jq -r '.values[].name'
      echo
    else
      echo "No repositories found containing the word '$word' in the project '$project'."
      echo
    fi
  done
done
