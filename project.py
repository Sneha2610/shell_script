import json

# Load the JSON data from a file (replace 'projects.json' with your actual JSON file name)
with open('projects.json', 'r') as json_file:
    data = json.load(json_file)

# Extract project names
project_names = [project['name'] for project in data['value']]

# Save project names to a text file
with open('projects.txt', 'w') as file:
    for name in project_names:
        file.write(name + '\n')

print("Project names have been saved to 'projects.txt'")
