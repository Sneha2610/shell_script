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

    try:
        # Read CSV with space handling
        df = pd.read_csv(csv_file, encoding="utf-8", skipinitialspace=True)  
        print(f"Processing {csv_file} - Found columns: {list(df.columns)}")  # Debugging line

        # Normalize column names (strip spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower()

        required_columns = {"line", "linenumber", "file"}  # Ensure lowercase match
        if not required_columns.issubset(df.columns):
            print(f"Skipping {csv_file} - Missing required columns.")
            return []

        incident_data = []
        for _, row in df.iterrows():
            secret_line = row["line"]
            line_number = row["linenumber"]
            file_path = row["file"]

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

    except Exception as e:
        print(f"Error processing {csv_file}: {e}")
        return []

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