import os
import pandas as pd
from bs4 import BeautifulSoup

# Folder containing all HTML reports
html_folder = "reports"  # Change to your actual folder path
output_csv = "consolidated_incidents.csv"

def parse_gitleaks_html(html_file):
    """Extracts data from a single Gitleaks HTML report."""
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract Project Name (Modify as needed)
    project_name = "Unknown Project"
    repo_name = os.path.basename(html_file).replace(".html", "")  # Extract repo name from filename

    meta_tags = soup.find_all("meta")
    for meta in meta_tags:
        if meta.get("name") == "project":
            project_name = meta.get("content")
        if meta.get("name") == "repo":
            repo_name = meta.get("content")  # If repo name is in metadata

    # Extract table data
    table = soup.find("table")  # Assuming a single relevant table
    if not table:
        print(f"No table found in {html_file}")
        return []

    rows = table.find_all("tr")[1:]  # Skip headers
    incident_data = []
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue  # Skip invalid rows

        secret_line = cols[2].text.strip()  # Extract the leaked variable/secret

        # Format data for CSV
        incident_data.append({
            "Incident Message": "Please ensure you rotate the credentials and update them",
            "Project Name": project_name,
            "Repository Name": repo_name,
            "Variables/Secrets to Remediate": secret_line,
            "Remediation Guide": "Link"  # Modify if a specific guide link is available
        })

    return incident_data

# Process all HTML reports in the folder
all_incidents = []
for filename in os.listdir(html_folder):
    if filename.endswith(".html"):
        file_path = os.path.join(html_folder, filename)
        all_incidents.extend(parse_gitleaks_html(file_path))

# Convert to CSV
if all_incidents:
    df = pd.DataFrame(all_incidents)
    df.to_csv(output_csv, index=False)
    print(f"Consolidated CSV Generated: {output_csv}")
else:
    print("No valid data extracted from HTML reports.")