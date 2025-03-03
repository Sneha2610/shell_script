import os
import pandas as pd

# Folder containing all Gitleaks CSV reports
csv_folder = "reports"
output_csv = "consolidated_incidents.csv"

# Hardcoded Project Name (Modify as needed)
PROJECT_NAME = "Your Project Name"

def process_gitleaks_csv(csv_file):
    """Extracts data from a single Gitleaks CSV report."""
    repo_name = os.path.basename(csv_file).replace("_gitleaks.csv", "")  # Extract repo name
    
    # Read Gitleaks CSV
    df = pd.read_csv(csv_file)

    # Check if required columns exist
    required_columns = {"Line", "LineNumber", "File"}  # Adjust based on actual CSV structure
    if not required_columns.issubset(df.columns):
        print(f"Skipping {csv_file} - Missing required columns.")
        return []

    incident_data = []
    
    for _, row in df.iterrows():
        secret_line = row["Line"]  # Extract leaked secret
        line_number = row["LineNumber"]  # Extract line number
        file_path = row["File"]  # Extract file path

        incident_data.append({
            "Incident Message": "Please ensure you rotate the credentials and update them",
            "Project Name": PROJECT_NAME,
            "Repository Name": repo_name,
            "Variables/Secrets to Remediate": secret_line,
            "Line Number": line_number,
            "File Path": file_path,
            "Remediation Guide": "Link"
        })

    return incident_data

# Process all CSV reports in the folder
all_incidents = []
for filename in os.listdir(csv_folder):
    if filename.endswith("_gitleaks.csv"):
        file_path = os.path.join(csv_folder, filename)
        all_incidents.extend(process_gitleaks_csv(file_path))

# Convert to CSV
if all_incidents:
    df = pd.DataFrame(all_incidents)
    df.to_csv(output_csv, index=False)
    print(f"Consolidated CSV Generated: {output_csv}")
else:
    print("No valid data extracted from CSV reports.")