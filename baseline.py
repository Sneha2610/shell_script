import json
import os
import shutil

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gitleaks Report</title>
    <script>
        function markAsFalsePositive(commit, file, secret) {
            let request = new XMLHttpRequest();
            request.open("POST", "/flag", true);
            request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            request.send(JSON.stringify({
                "commit": commit,
                "file": file,
                "secret": secret
            }));
            document.getElementById(commit + file).innerHTML = "Flagged as False Positive";
        }
    </script>
</head>
<body>
    <h1>Gitleaks Report</h1>
    <table border="1">
        <thead>
            <tr>
                <th>Commit</th>
                <th>File</th>
                <th>Match</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {{ rows }}
        </tbody>
    </table>
</body>
</html>
"""

ROW_TEMPLATE = """
<tr>
    <td>{commit}</td>
    <td>{file}</td>
    <td>{secret}</td>
    <td id="{commit}{file}">
        <button onclick="markAsFalsePositive('{commit}', '{file}', '{secret}')">Flag as False Positive</button>
    </td>
</tr>
"""

def generate_html_report(json_report_path, output_html_path):
    # Load the Gitleaks report
    with open(json_report_path, 'r') as f:
        report_data = json.load(f)

    # Assuming 'Match' is part of each finding in the JSON structure
    if isinstance(report_data, list):
        findings = report_data
    else:
        print("The Gitleaks report does not contain any findings.")
        return

    rows = ""
    for finding in findings:
        commit = finding.get('Commit', 'N/A')  # Get the commit ID
        file = finding.get('File', 'N/A')      # Get the file path
        secret = finding.get('Match', 'N/A')   # Get the matched secret
        rows += ROW_TEMPLATE.format(commit=commit, file=file, secret=secret)

    html_content = HTML_TEMPLATE.replace('{{ rows }}', rows)

    # Write the HTML content to the output file
    with open(output_html_path, 'w') as f:
        f.write(html_content)

def update_baseline(baseline_file, flagged_false_positives):
    if os.path.exists(baseline_file):
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
    else:
        baseline_data = {"false_positives": []}

    baseline_data["false_positives"].extend(flagged_false_positives)

    with open(baseline_file, 'w') as f:
        json.dump(baseline_data, f, indent=4)

def clear_old_reports():
    report_dir = "reports"
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir)
    os.makedirs(report_dir)

if __name__ == "__main__":
    # Generate HTML report from Gitleaks JSON
    generate_html_report('gitleaks_report.json', 'reports/gitleaks_report.html')

    # Optionally update baseline with flagged false positives (assumed to be gathered interactively)
    flagged_false_positives = []  # You can update this part with actual false positives later
    update_baseline('baseline.json', flagged_false_positives)

    # Clear old reports (optional)
    clear_old_reports()
