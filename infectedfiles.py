import re

def extract_summary(log_file):
    summary = {}
    infected_files = []
    with open(log_file, 'r') as file:
        log_content = file.read()

        # Extract summary information
        summary['known_viruses'] = re.search(r'Known viruses:\s+(\d+)', log_content).group(1)
        summary['engine_version'] = re.search(r'Engine version:\s+([\d.]+)', log_content).group(1)
        summary['scanned_directories'] = re.search(r'Scanned directories:\s+(\d+)', log_content).group(1)
        summary['scanned_files'] = re.search(r'Scanned files:\s+(\d+)', log_content).group(1)
        summary['infected_files'] = re.search(r'Infected files:\s+(\d+)', log_content).group(1)
        summary['data_scanned'] = re.search(r'Data scanned:\s+([\d.]+\s+\w+)', log_content).group(1)
        summary['data_read'] = re.search(r'Data read:\s+([\d.]+\s+\w+)', log_content).group(1)
        summary['time'] = re.search(r'Time:\s+([\d.]+\s+sec\s+\([\d\w\s]+\))', log_content).group(1)
        
        # Extract infected file details
        infected_pattern = re.compile(r'^(.*):\s+(\w+)\s+FOUND$', re.MULTILINE)
        infected_files = infected_pattern.findall(log_content)
        
    return summary, infected_files

def generate_html_report(summary, infected_files):
    html_content = f"""
    <html>
    <head>
        <title>ClamAV Scan Report</title>
        <style>
            table {{
                font-family: Arial, sans-serif;
                border-collapse: collapse;
                width: 50%;
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
                width: 80%;
                margin: 20px auto;
            }}
        </style>
    </head>
    <body>
        <h2>ClamAV Scan Summary</h2>
        <table>
            <tr><th>Attribute</th><th>Value</th></tr>
            <tr><td>Known Viruses</td><td>{summary['known_viruses']}</td></tr>
            <tr><td>Engine Version</td><td>{summary['engine_version']}</td></tr>
            <tr><td>Scanned Directories</td><td>{summary['scanned_directories']}</td></tr>
            <tr><td>Scanned Files</td><td>{summary['scanned_files']}</td></tr>
            <tr><td>Infected Files</td><td>{summary['infected_files']}</td></tr>
            <tr><td>Data Scanned</td><td>{summary['data_scanned']}</td></tr>
            <tr><td>Data Read</td><td>{summary['data_read']}</td></tr>
            <tr><td>Time</td><td>{summary['time']}</td></tr>
        </table>
        <h2>Infected Files</h2>
        <table class="infected-files">
            <tr><th>File</th><th>Malware</th></tr>"""
    
    for file, malware in infected_files:
        html_content += f"<tr><td>{file}</td><td>{malware}</td></tr>"
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open("clamav_report.html", "w") as report_file:
        report_file.write(html_content)

# Extract summary and generate report
log_file_path = 'clamav.log'
summary, infected_files = extract_summary(log_file_path)
generate_html_report(summary, infected_files)
