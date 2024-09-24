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
    """Compares two lists of dictionaries and returns added and removed rows."""
    set1 = set(tuple(sorted(row.items())) for row in data1)
    set2 = set(tuple(sorted(row.items())) for row in data2)

    added = set2 - set1  # Rows added to folder2
    removed = set1 - set2  # Rows removed from folder1

    return added, removed

def write_comparison_csv(file_name, added, removed, output_dir, fieldnames):
    """Writes the comparison result to a CSV file with an extra column for changes."""
    output_file = os.path.join(output_dir, f"comparison_{file_name}")

    # Add an extra column "Change" to indicate where the row was added/removed
    fieldnames.append('Change')

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in added:
            row_dict = dict(row)
            row_data = {key: value for key, value in row_dict}
            row_data['Change'] = 'Added in folder2'
            writer.writerow(row_data)

        for row in removed:
            row_dict = dict(row)
            row_data = {key: value for key, value in row_dict}
            row_data['Change'] = 'Removed from folder1'
            writer.writerow(row_data)

    print(f"Comparison report saved: {output_file}")

def append_to_summary_csv(summary_file, file_name, added, removed, fieldnames):
    """Appends the comparison summary of a single file to the summary CSV."""
    fieldnames.append('Change')

    with open(summary_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Check if the file is empty and write the header if needed
        if f.tell() == 0:
            writer.writeheader()

        for row in added:
            row_dict = dict(row)
            row_data = {key: value for key, value in row_dict}
            row_data['Change'] = 'Added in folder2'
            row_data['file_name'] = file_name
            writer.writerow(row_data)

        for row in removed:
            row_dict = dict(row)
            row_data = {key: value for key, value in row_dict}
            row_data['Change'] = 'Removed from folder1'
            row_data['file_name'] = file_name
            writer.writerow(row_data)

def compare_csv_files_in_folders(folder1, folder2, output_dir):
    """Compares CSV files with common names in two folders and generates comparison reports."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a summary comparison CSV file
    summary_file = os.path.join(output_dir, "summary_comparison.csv")

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

        # Get the fieldnames (column headers)
        fieldnames = data1[0].keys() if data1 else data2[0].keys()

        # Compare the data
        added, removed = compare_csv_data(data1, data2)

        # Write comparison result to CSV with "Change" column
        write_comparison_csv(file_name, added, removed, output_dir, list(fieldnames))

        # Append the changes to the summary CSV
        append_to_summary_csv(summary_file, file_name, added, removed, list(fieldnames))

    print(f"Comparison completed. Individual reports and summary saved in {output_dir}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compare CSV files from two folders and generate comparison reports.")
    parser.add_argument('--folder1', required=True, help="Path to the first folder containing CSV files")
    parser.add_argument('--folder2', required=True, help="Path to the second folder containing CSV files")
    parser.add_argument('--output-dir', required=True, help="Output directory to save the comparison CSV files")
    
    args = parser.parse_args()

    # Run the comparison
    compare_csv_files_in_folders(args.folder1, args.folder2, args.output_dir)
