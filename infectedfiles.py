import json

# Sample data structure (replace with your actual data or read from file)
scan_summary = {
    "Known Viruses": 1234567,
    "Engine Version": "0.103.2",
    "Scanned Directories": 25,
    "Scanned Files": 100,
    "Infected Files": 2,
    "Data Scanned": "15.23 MB",
    "Data Read": "10.45 MB",
    "Time": "0.005 sec (0 m 0 s)"
}

scanned_files = [
    {"File": "/path/to/file1", "Virus Found": "No"},
    {"File": "/path/to/file2", "Virus Found": "Yes"},
    {"File": "/path/to/file3", "Virus Found": "No"},
    {"File": "/path/to/file4", "Virus Found": "Yes"}
]

# Generate HTML report
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
                text-a
