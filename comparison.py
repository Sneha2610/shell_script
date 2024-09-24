import os
import csv
import argparse

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

def main(first_dir, second_dir, output_file):
    # Create or open the output CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['repo', 'added_leaks', 'removed_leaks']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate through CSV files in the first directory
        for root, _, files in os.walk(first_dir):
            for file in files:
                if file.endswith('.csv'):
                    repo_name = os.path.basename(file)
                    first_file = os.path.join(first_dir, file)
                    second_file = os.path.join(second_dir, file)

                    # Check if the second report for the same repo exists
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Compare Gitleaks scan reports")
    parser.add_argument('--first-dir', required=True, help="Directory of first Gitleaks scan report CSVs")
    parser.add_argument('--second-dir', required=True, help="Directory of second Gitleaks scan report CSVs")
    parser.add_argument('--output', required=True, help="Output CSV file for comparison results")
    
    args = parser.parse_args()

    # Run the comparison process
    main(args.first_dir, args.second_dir, args.output)
