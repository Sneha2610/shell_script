import os
import csv

# Input CSV containing the list of IPs (column name: "IP")
IP_CSV_FILE = "ip_list.csv"

# Directory to scan
SCAN_DIR = "."

# Output CSV file
OUTPUT_CSV = "ip_scan_report.csv"

def load_ip_list():
    """Load IPs from the 'IP' column of the CSV file."""
    ip_list = set()
    try:
        with open(IP_CSV_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)  # Use DictReader to access the "IP" column
            for row in reader:
                ip = row.get("IP", "").strip()
                if ip:
                    ip_list.add(ip)
    except Exception as e:
        print(f"Error reading IP list CSV: {e}")
    
    return ip_list

def scan_files_for_ips(ip_list):
    """Scan repository files for occurrences of the given IPs."""
    found_ips = []

    for root, _, files in os.walk(SCAN_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Check for each IP in the file content
                    for ip in ip_list:
                        if ip in content:
                            found_ips.append([file_path, ip])
            except Exception as e:
                print(f"Skipping file {file_path}: {e}")
    
    return found_ips

def generate_csv_report(ips):
    """Generate a CSV report if any IPs are found."""
    if ips:
        with open(OUTPUT_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File Path", "Found IP"])
            writer.writerows(ips)
        print(f"IP Scan report generated: {OUTPUT_CSV}")
    else:
        print("No IPs found in the repository.")

if __name__ == "__main__":
    ip_list = load_ip_list()
    if not ip_list:
        print("No IPs found in the list. Exiting...")
    else:
        found_ips = scan_files_for_ips(ip_list)
        generate_csv_report(found_ips)