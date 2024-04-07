import json

def load_json(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data

def generate_html(json_data):
    """Generate HTML report based on JSON data."""
    summary = json_data.get('summary', {})

    # Define HTML template with embedded CSS styles
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Scan Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #f9f9f9;
        }
        table {
            width: 50%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            width: 30%;
        }
        .severity-low {
            color: yellow;
        }
        .severity-medium {
            color: orange;
        }
        .severity-high {
            color: red;
        }
        .severity-critical {
            color: maroon;
        }
    </style>
</head>
<body>
    <h1>ML Scan Summary</h1>
    <table>
        <tr>
            <th>Total Issues by Severity</th>
            <td class="severity-low">LOW: {low_count}</td>
            <td class="severity-medium">MEDIUM: {medium_count}</td>
            <td class="severity-high">HIGH: {high_count}</td>
            <td class="severity-critical">CRITICAL: {critical_count}</td>
        </tr>
        <tr>
            <th>Total Issues</th>
            <td colspan="4">{total_issues}</td>
        </tr>
        <tr>
            <th>Input Path</th>
            <td colspan="4">{input_path}</td>
        </tr>
        <tr>
            <th>Absolute Path</th>
            <td colspan="4">{absolute_path}</td>
        </tr>
        <tr>
            <th>ModelScan Version</th>
            <td colspan="4">{modelscan_version}</td>
        </tr>
        <tr>
            <th>Timestamp</th>
            <td colspan="4">{timestamp}</td>
        </tr>
        <tr>
            <th>Total Scanned</th>
            <td colspan="4">{total_scanned}</td>
        </tr>
        <tr>
            <th>Total Skipped</th>
            <td colspan="4">{total_skipped}</td>
        </tr>
        <tr>
            <th>Skipped Files</th>
            <td colspan="4">{skipped_files}</td>
        </tr>
    </table>
</body>
</html>
"""

    # Extract values from JSON data
    low_count = summary['total_issues_by_severity'].get('LOW', 0)
    medium_count = summary['total_issues_by_severity'].get('MEDIUM', 0)
    high_count = summary['total_issues_by_severity'].get('HIGH', 0)
    critical_count = summary['total_issues_by_severity'].get('CRITICAL', 0)
    total_issues = summary.get('total_issues', 0)
    input_path = summary.get('input path', '')
    absolute_path = summary.get('absolute_path', '')
    modelscan_version = summary.get('modelscan_version', '')
    timestamp = summary.get('timestamp', '')
    total_scanned = summary['scanned'].get('total_scanned', 0)
    total_skipped = summary['skipped'].get('total_skipped', 0)
    skipped_files = ', '.join(summary['skipped'].get('skipped_files', []))

    # Replace placeholders with extracted values in the HTML template
    html_content = html_template.format(
        low_count=low_count,
        medium_count=medium_count,
        high_count=high_count,
        critical_count=critical_count,
        total_issues=total_issues,
        input_path=input_path,
        absolute_path=absolute_path,
        modelscan_version=modelscan_version,
        timestamp=timestamp,
        total_scanned=total_scanned,
        total_skipped=total_skipped,
        skipped_files=skipped_files
    )

    return html_content

def save_html(html_content, output_path):
    """Save HTML content to file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
    json_file_path = 'MLscan.json'  # Path to your JSON file
    html_output_path = 'MLscan.html'  # Output path for HTML file

    json_data = load_json(json_file_path)
    html_content = generate_html(json_data)
    save_html(html_content, html_output_path)

if __name__ == '__main__':
    main()
