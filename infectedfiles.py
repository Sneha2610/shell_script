import re

def extract_summary(log_file):
    summary = {}
    scanned_files = []
    
    # Regex patterns
    summary_pattern = re.compile(
        r'Known viruses:\s+(\d+)|Engine version:\s+([\d.]+)|Scanned directories:\s+(\d+)|'
        r'Scanned files:\s+(\d+)|Infected files:\s+(\d+)|Data scanned:\s+([\d.]+\s+\w+)|'
        r'Data read:\s+([\d.]+\s+\w+)|Time:\s+([\d.]+\s+sec\s+\([\d\w\s]+\))'
    )
    scanned_pattern = re.compile(r'^(.*?):\s+(.*?\sFOUND|OK)$', re.MULTILINE)
    
    with open(log_file, 'r') as file:
        log_content = file.read()

        # Extract summary information
        for match in summary_pattern.finditer(log_content):
            if match.group(1):
                summary['known_viruses'] = match.group(1)
            if match.group(2):
                summary['engine_version'] = match.group(2)
            if match.group(3):
                summary['scanned_directories'] = match.group(3)
            if match.group(4):
                summary['scanned_files'] = match.group(4)
            if match.group(5):
                summary['infected_files'] = match.group(5)
            if match.group(6):
                summary['data_scanned'] = match.group(6)
            if match.group(7):
                summary['data_read'] = match.group(7)
            if match.group(8):
                summary['time'] = match.group(8)
        
        # Extract scanned file details
        scanned_files = scanned_pattern.findall(log_content)
        
    return summary, scanned_files

def generate_html_report(summary, scanned_files):
    html_content = f"""
    <html>
    <head>
        <title>ClamAV Scan Report</title>
        <style>
            table {{
                font-family: Arial, sans-serif;
                border-collapse: collapse;
                width: 80%;
                margin: 20px auto;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .infected-files {{
                border-collapse: collapse;
                width: 80%;
                margin: 20px auto;
            }}
            .infected-files th, .infected-files td {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
            .infected-files th {{
                background-color: #f2f2f2;
                color: red;
            }}
        </style>
    </head>
    <body>
        <h2>ClamAV Scan Summary</h2>
        <table>
            <tr><th>Attribute</th><th>Value</th></tr>
            <tr><td>Known Viruses</td><td>{summary.get('known_viruses', 'N/A')}</td></tr>
            <tr><td>Engine Version</td><td>{summary.get('engine_version', 'N/A')}</td></tr>
            <tr><td>Scanned Directories</td><td>{summary.get('scanned_directories', 'N/A')}</td></tr>
            <tr><td>Scanned Files</td><td>{summary.get('scanned_files', 'N/A')}</td></tr>
            <tr><td>Infected Files</td><td>{summary.get('infected_files', 'N/A')}</td></tr>
            <tr><td>Data Scanned</td><td>{summary.get('data_scanned', 'N/A')}</td></tr>
            <tr><td>Data Read</td><td>{summary.get('data_read', 'N/A')}</td></tr>
            <tr><td>Time</td><td>{summary.get('time', 'N/A')}</td></tr>
        </table>
        <h2>Scanned Files</h2>
        <table class="scanned-files">
            <tr><th>File</th><th>Virus Found</th></tr>"""
    
    for file, status in scanned_files:
        virus_found = "Yes" if "FOUND" in status else "No"
        html_content += f"<tr><td>{file}</td><td>{virus_found}</td></tr>"
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open("clamav_report.html", "w") as report_file:
        report_file.write(html_content)

# Extract summary and generate report
log_file_path = 'clam.log'
summary, scanned_files = extract_summary(log_file_path)
generate_html_report(summary, scanned_files)
