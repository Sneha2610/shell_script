import os
import csv
import argparse

def read_csv(file_path):
    """Reads a CSV file and returns its content as a list of dictionaries."""
    data = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compare_csv_data(data1, data2):
    """Compares two lists of dictionaries and returns added, removed, and changed rows."""
    set1 = set(tuple(sorted(row.items())) for row in data1)
    set2 = set(tuple(sorted(row.items())) for row in data2)

    added = set2 - set1
    removed = set1 - set2

    return added, removed

def write_comparison_csv(file_name, added, removed, output_dir):
    """Writes the comparison result to a CSV file."""
    output_file = os.path.join(output_dir, f"comparison_{file_name}")

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['type', 'content']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in added:
            writer.writerow({'type': 'added', 'content': dict(row)})

        for row in removed:
            writer.writerow({'type': 'removed', 'content': dict(row)})

    print(f"Comparison report saved: {output_file}")

def compare_csv_files_in_folders(folder1, folder2, output_dir):
    """Compares CSV files with common names in two folders and generates comparison reports."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # List CSV files in both folders
    folder1_files = {file for file in os.listdir(folder1) if file.endswith('.csv')}
    folder2_files = {file for file in os.listdir(folder2) if file.endswith('.csv')}

    # Find common files between the two folders
    common_files = folder1_files.intersection(folder2_files)

    # Compare each common CSV file
    for file_name in common_files:
        file1_path = os.path.join(folder1, file_name)
        file2_path = os.path.join(folder2, file_name)

        # Read CSV files
        data1 = read_csv(file1_path)
        data2 = read_csv(file2_path)

        # Compare the data
        added, removed = compare_csv_data(data1, data2)

        # Write comparison result to CSV
        write_comparison_csv(file_name, added, removed, output_dir)

    print(f"Comparison completed. Reports saved in {output_dir}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compare CSV files from two folders and generate comparison reports.")
    parser.add_argument('--folder1', required=True, help="Path to the first folder containing CSV files")
    parser.add_argument('--folder2', required=True, help="Path to the second folder containing CSV files")
    parser.add_argument('--output-dir', required=True, help="Output directory to save the comparison CSV files")
    
    args = parser.parse_args()

    # Run the comparison
    compare_csv_files_in_folders(args.folder1, args.folder2, args.output_dir)
