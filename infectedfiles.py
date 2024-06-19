import re
import json

# Function to extract scan summary from log
def extract_scan_summary(log):
    match = re.search(r'ClamAV Scan Summary:(.*)\[', log, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    else:
        return None

# Function to extract scanned files from log
def extract_scanned_files(log):
    match = re.search(r'Scanned Files:(.*)', log, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    else:
        return None

# Function to generate HTML report
def generate_html_report(scan_summary, scanned_files):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClamAV Scan Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                padding: 20px;
            }
            h2 {
                color: #333;
            }
            .container {
                max-width: 800px; /* Adjust max-width as needed */
                margin: 0 auto; /* Center align container */
            }
            .summary-table, .scanned-files {
                width: 100%;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            .summary-table th, .summary-table td, .scanned-files th, .scanned-files td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .summary-table th {
                background-color: #f2f2f2;
                color: #333;
            }
            .scanned-files th {
                background-color: #e57373;
                color: #fff;
            }
            .scanned-files td {
                background-color: #ffcdd2;
                color: #333;
            }
            .highlight {
                color: red;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>ClamAV Scan Summary</h2>
            <table class="summary-table">
                <tr><th>Attribute</th><th>Value</th></tr>
    """

    # Populate summary table
    for key, value in scan_summary.items():
        html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"

    html_content += """
            </table>

            <h2>Scanned Files</h2>
            <table class="scanned-files">
                <tr><th>File</th><th>Virus Found</th></tr>
    """

    # Populate scanned files table
    for file_data in scanned_files:
        virus_found = file_data["Virus Found"]
        if virus_found == "Yes":
            html_content += f'<tr><td>{file_data["File"]}</td><td class="highlight">{virus_found}</td></tr>'
        else:
            html_content += f'<tr><td>{file_data["File"]}</td><td>{virus_found}</td></tr>'

    html_content += """
            </table>
        </div>
    </body>
    </html>
    """

    return html_content

# Function to read ClamAV log file
def read_clamav_log(log_file):
    with open(log_file, 'r') as file:
        return file.read()

# Main function to generate report
def main():
    # Specify path to ClamAV log file
    log_file = 'clam.log'

    # Read ClamAV log data
    clam_log = read_clamav_log(log_file)

    # Extract scan summary and scanned files
    scan_summary = extract_scan_summary(clam_log)
    scanned_files = extract_scanned_files(clam_log)

    # Generate HTML report
    if scan_summary and scanned_files:
        report_html = generate_html_report(scan_summary, scanned_files)

        # Write HTML report to a file
        with open("clamav_scan_report.html", "w") as file:
            file.write(report_html)

        print("HTML report generated successfully.")
    else:
        print("Failed to extract scan summary or scanned files from the ClamAV log.")

if __name__ == "__main__":
    main()
