import os
import zipfile
import csv
from bs4 import BeautifulSoup  # For parsing HTML

def extract_gitleaks_reports(zip_file, output_csv):
    # Create a list to hold extracted data
    extracted_data = []

    # Open the zip file
    with zipfile.ZipFile(zip_file, 'r') as z:
        # List all files in the zip
        file_list = z.namelist()

        # Loop through each HTML file in the zip
        for file in file_list:
            if file.endswith(".html"):  # We only care about HTML files
                # Read the HTML content
                with z.open(file) as f:
                    soup = BeautifulSoup(f, 'html.parser')

                    # Extract Repository Name from the filename (or alternatively from HTML content)
                    repo_name = os.path.basename(file).replace(".html", "")

                    # Extract the Leaks Found Count (modify this based on the structure of the HTML)
                    leaks_found = 0
                    leaks_section = soup.find("h2", text="Leaks Found")
                    if leaks_section:
                        leaks_found = int(leaks_section.find_next("p").text.strip())

                    # Check if whitelist is found (this assumes 'whitelist' is mentioned somewhere in the HTML)
                    whitelisting_found = "No"
                    if "whitelist" in soup.text.lower():
                        whitelisting_found = "Yes"

                    # Append the data
                    extracted_data.append([repo_name, leaks_found, whitelisting_found])

    # Write the data to a CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write the header
        csvwriter.writerow(['Repository Name', 'Leaks Found', 'Whitelisting Found'])
        # Write the data rows
        csvwriter.writerows(extracted_data)

    print(f"CSV report generated: {output_csv}")

# Example usage
zip_file_path = 'path/to/gitleaks_reports.zip'  # Replace with your actual zip file path
output_csv_path = 'gitleaks_report_summary.csv'  # Output CSV file path
extract_gitleaks_reports(zip_file_path, output_csv_path)
