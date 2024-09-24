import os
import zipfile
import argparse
import csv

def unzip_file(zip_path, extract_to):
    """Unzips a file to a specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_csv(file_path):
    """Reads a CSV file and returns its content as a list of dictionaries."""
    leaks = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leaks.append(row)
    return leaks

def compare_reports(first_report, second_report):
    """Compares two Gitleaks CSV reports and identifies added and removed leaks."""
    first_leaks = set(tuple(sorted(row.items())) for row in first_report)
    second_leaks = set(tuple(sorted(row.items())) for row in second_report)

    added_leaks = second_leaks - first_leaks
    removed_leaks = first_leaks - second_leaks

    return added_leaks, removed_leaks

def write_comparison_result(repo_name, added_leaks, removed_leaks, writer):
    """Writes the comparison results for a single repo to the output CSV."""
    writer.writerow({
        'repo': repo_name,
        'added_leaks': len(added_leaks),
        'removed_leaks': len(removed_leaks)
    })

def main(report1_zip, report2_zip, output_file):
    # Create temporary directories to extract reports
    report1_dir = "./report1"
    report2_dir = "./report2"
    
    os.makedirs(report1_dir, exist_ok=True)
    os.makedirs(report2_dir, exist_ok=True)

    # Step 1: Unzip the files
    unzip_file(report1_zip, report1_dir)
    unzip_file(report2_zip, report2_dir)

    # Step 2: Create or open the output CSV file for comparison results
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['repo', 'added_leaks', 'removed_leaks']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Step 3: Iterate through CSV files in the first directory
        for root, _, files in os.walk(report1_dir):
            for file in files:
                if file.endswith('.csv'):
                    repo_name = os.path.basename(file)
                    first_file = os.path.join(report1_dir, file)
                    second_file = os.path.join(report2_dir, file)

                    # Step 4: Check if the second report for the same repo exists
                    if os.path.exists(second_file):
                        # Read both CSV reports
                        first_report = read_csv(first_file)
                        second_report = read_csv(second_file)

                        # Compare reports and identify differences
                        added_leaks, removed_leaks = compare_reports(first_report, second_report)

                        # Write comparison results to the output CSV
                        write_comparison_result(repo_name, added_leaks, removed_leaks, writer)
                    else:
                        print(f"Warning: {repo_name} not found in second report directory.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compare Gitleaks scan reports")
    parser.add_argument('--report1-zip', required=True, help="Path to the first Gitleaks report zip file")
    parser.add_argument('--report2-zip', required=True, help="Path to the second Gitleaks report zip file")
    parser.add_argument('--output', required=True, help="Output CSV file for comparison results")
    
    args = parser.parse_args()

    # Run the comparison process
    main(args.report1_zip, args.report2_zip, args.output)
