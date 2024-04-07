import json

# JSON data
json_data = '''
{
    "summary": {
        "total_issues_by_severity": {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        },
        "total_issues": 0,
        "input path": "saved_model.pb",
        "absolute_path": "/apps/ado-agent/adoagent/_work/1/s",
        "modelscan_version": "0.7.0",
        "timestamp": "2024-04-02T08:44:05.623188",
        "scanned": {
            "total_scanned": 0
        },
        "skipped": {
            "total_skipped": 0,
            "skipped_files": []
        }
    }
}
'''

# Parse JSON
data = json.loads(json_data)

# Extract required fields
total_low = data["summary"]["total_issues_by_severity"]["LOW"]
total_medium = data["summary"]["total_issues_by_severity"]["MEDIUM"]
total_high = data["summary"]["total_issues_by_severity"]["HIGH"]
total_critical = data["summary"]["total_issues_by_severity"]["CRITICAL"]
total_issues = data["summary"]["total_issues"]
input_path = data["summary"]["input path"]
absolute_path = data["summary"]["absolute_path"]
modelscan_version = data["summary"]["modelscan_version"]
timestamp = data["summary"]["timestamp"]
total_scanned = data["summary"]["scanned"]["total_scanned"]
total_skipped = data["summary"]["skipped"]["total_skipped"]
skipped_files = ", ".join(data["summary"]["skipped"]["skipped_files"])

# Generate HTML content
html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSON to HTML Conversion</title>
</head>
<body>
    <h1>Summary Information</h1>
    <ul>
        <li>Total Issues by Severity:</li>
        <ul>
            <li>LOW: {total_low}</li>
            <li>MEDIUM: {total_medium}</li>
            <li>HIGH: {total_high}</li>
            <li>CRITICAL: {total_critical}</li>
        </ul>
        <li>Total Issues: {total_issues}</li>
        <li>Input Path: {input_path}</li>
        <li>Absolute Path: {absolute_path}</li>
        <li>ModelScan Version: {modelscan_version}</li>
        <li>Timestamp: {timestamp}</li>
        <li>Total Scanned: {total_scanned}</li>
        <li>Total Skipped: {total_skipped}</li>
        <li>Skipped Files: {skipped_files}</li>
    </ul>
</body>
</html>
'''

# Write HTML content to a file
with open('output.html', 'w') as html_file:
    html_file.write(html_content)
