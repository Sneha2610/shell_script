import os
import pandas as pd
import zipfile

def extract_zip(zip_path, extract_to):
    """Extract a zip file to a given folder."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def get_csv_files(folder):
    """Get a list of CSV files in a specified folder."""
    return [file for file in os.listdir(folder) if file.endswith('.csv')]

def read_csv_data(file_path):
    """Read a CSV file and return its DataFrame, handling empty files."""
    if os.path.getsize(file_path) == 0:
        print(f"Warning: The file '{file_path}' is empty.")
        return pd.DataFrame()  # Return an empty DataFrame
    return pd.read_csv(file_path)

def compare_csv_files(folder1, folder2, output_folder):
    """Compare CSV files in two folders and generate comparison reports."""
    folder1_files = get_csv_files(folder1)
    folder2_files = get_csv_files(folder2)

    for file in folder1_files:
        if file in folder2_files:
            df1 = read_csv_data(os.path.join(folder1, file))
            df2 = read_csv_data(os.path.join(folder2, file))

            if df1.empty or df2.empty:
                print(f"Skipping comparison for {file} due to empty data.")
                continue

            # Perform an outer join on all columns
            comparison_df = pd.merge(df1, df2, on=list(df1.columns), how='outer', indicator=True)

            # Add Availability Columns for each report
            comparison_df['Availability in reportV7'] = comparison_df['_merge'].map({
                'left_only': 'Available',
                'right_only': 'Unavailable',
                'both': 'Available'
            })
            comparison_df['Availability in reportV8'] = comparison_df['_merge'].map({
                'left_only': 'Unavailable',
                'right_only': 'Available',
                'both': 'Available'
            })

            # Drop the '_merge' column used by pd.merge
            comparison_df.drop(columns=['_merge'], inplace=True)

            # Save the comparison result
            output_file = os.path.join(output_folder, f'comparison_{file}')
            comparison_df.to_csv(output_file, index=False)
            print(f"Comparison report saved for {file} at {output_file}")

# Paths for zip files and extraction folders
reportv7_zip = 'path_to_reportv7.zip'
reportv8_zip = 'path_to_reportv8.zip'

folder1 = 'path_to_extract_reportv7'  # Folder to extract reportv7.zip
folder2 = 'path_to_extract_reportv8'  # Folder to extract reportv8.zip
output_folder = 'path_to_output_comparisons'  # Folder to save the comparison reports

# Extract the zip files
extract_zip(reportv7_zip, folder1)
extract_zip(reportv8_zip, folder2)

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Compare CSV files and save comparison reports
compare_csv_files(folder1, folder2, output_folder)

print("Comparison completed for all common CSV files.")
