import json

def load_json(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data

def generate_html(json_data):
    summary = json_data.get('summary', {})

    # Define the HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scan Report</title>
    </head>
    <body>
        <h1>Scan Summary</h1>
        <ul>
            <li>Total Issues by Severity:</li>
            <ul>
                <li>LOW: {low_count}</li>
                <li>MEDIUM: {medium_count}</li>
                <li>HIGH: {high_count}</li>
                <li>CRITICAL: {critical_count}</li>
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
    """

    # Extract values from JSON data
    low_count = summary['total_issues_by_severity'].get('LOW') if 'total_issues_by_severity' in summary else None
    medium_count = summary['total_issues_by_severity'].get('MEDIUM') if 'total_issues_by_severity' in summary else None
    high_count = summary['total_issues_by_severity'].get('HIGH') if 'total_issues_by_severity' in summary else None
    critical_count = summary['total_issues_by_severity'].get('CRITICAL') if 'total_issues_by_severity' in summary else None
    total_issues = summary.get('total_issues')
    input_path = summary.get('input path')
    absolute_path = summary.get('absolute_path')
    modelscan_version = summary.get('modelscan_version')
    timestamp = summary.get('timestamp')
    total_scanned = summary['scanned'].get('total_scanned') if 'scanned' in summary else None
    total_skipped = summary['skipped'].get('total_skipped') if 'skipped' in summary else None
    skipped_files = ', '.join(summary['skipped'].get('skipped_files', [])) if 'skipped' in summary else None

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
    with open(output_path, 'w') as file:
        file.write(html_content)

def main():
    json_file_path = 'data.json'  # Path to your JSON file
    html_output_path = 'output.html'  # Output path for HTML file

    json_data = load_json(json_file_path)
    html_content = generate_html(json_data)
    save_html(html_content, html_output_path)

if __name__ == '__main__':
    main()
