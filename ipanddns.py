import os
import csv

# Input CSVs containing the list of IPs and DNS names
IP_CSV_FILE = "ip_list.csv"
DNS_CSV_FILE = "dns_list.csv"

# Get the scan directory from an environment variable (fallback to current directory)
SCAN_DIR = os.getenv("SCAN_DIR", ".")

# Output CSV file
OUTPUT_CSV = "ip_dns_scan_report.csv"

def load_list_from_csv(file_path, column_name):
    """Load values from the specified column of a CSV file."""
    values = set()
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                value = row.get(column_name, "").strip()
                if value:
                    values.add(value)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return values

def scan_files_for_patterns(patterns):
    """Scan repository files for occurrences of the given IPs/DNS names."""
    found_patterns = []

    for root, _, files in os.walk(SCAN_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Check for each pattern (IP/DNS) in the file content
                    for pattern in patterns:
                        if pattern in content:
                            found_patterns.append([file_path, pattern])
            except Exception as e:
                print(f"Skipping file {file_path}: {e}")
    
    return found_patterns

def generate_csv_report(found_data):
    """Generate a CSV report if any patterns (IPs/DNS) are found."""
    if found_data:
        with open(OUTPUT_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File Path", "Found Pattern"])
            writer.writerows(found_data)
        print(f"Scan report generated: {OUTPUT_CSV}")
    else:
        print("No matches found in the repository.")

if __name__ == "__main__":
    # Load IPs and DNS names
    ip_list = load_list_from_csv(IP_CSV_FILE, "IP")
    dns_list = load_list_from_csv(DNS_CSV_FILE, "DNS")

    # Combine both lists
    search_patterns = ip_list.union(dns_list)

    if not search_patterns:
        print("No IPs or DNS names found in the lists. Exiting...")
    else:
        found_patterns = scan_files_for_patterns(search_patterns)
        generate_csv_report(found_patterns)