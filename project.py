import json

# Load the JSON data (replace 'your_json_data' with your actual JSON data)
json_data = '''{
    "value": [
        {
            "id": "project-id-1",
            "name": "Project Name 1"
        },
        {
            "id": "project-id-2",
            "name": "Project Name 2"
        }
    ],
    "count": 2
}'''

data = json.loads(json_data)

# Extract project names
project_names = [project['name'] for project in data['value']]

# Save project names to a text file
with open('projects.txt', 'w') as file:
    for name in project_names:
        file.write(name + '\n')

print("Project names have been saved to 'projects.txt'")
