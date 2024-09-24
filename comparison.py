import os
import pandas as pd

def get_csv_files(folder):
    """Get a list of CSV files in a specified folder."""
    return [file for file in os.listdir(folder) if file.endswith('.csv')]

def read_csv_data(file_path):
    """Read a CSV file and return its DataFrame, handling empty files."""
    if os.path.getsize(file_path) == 0:
        print(f"Warning: The file '{file_path}' is empty.")
        return pd.DataFrame()  # Return an empty DataFrame if the file is empty
    return pd.read_csv(file_path)

def align_data_types(df1, df2):
    """Ensure the data types are aligned between two DataFrames."""
    common_columns = df1.columns.intersection(df2.columns)
    for col in common_columns:
        if df1[col].dtype != df2[col].dtype:
            # Convert to string if the types are mismatched to avoid merge issues
            df1[col] = df1[col].astype(str)
            df2[col] = df2[col].astype(str)
    return df1, df2

def compare_csv_files(folder1, folder2, output_folder):
    """Compare CSV files in two folders and generate comparison reports."""
    folder1_files = get_csv_files(folder1)
    folder2_files = get_csv_files(folder2)

    # Ensure that all CSV files from both folders are considered
    all_files = set(folder1_files).union(set(folder2_files))

    for file in all_files:
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()

        # Load the CSV from folder1 if it exists, otherwise create an empty DataFrame
        if file in folder1_files:
            df1 = read_csv_data(os.path.join(folder1, file))
        else:
            print(f"File {file} not found in folder1, treating as empty.")

        # Load the CSV from folder2 if it exists, otherwise create an empty DataFrame
        if file in folder2_files:
            df2 = read_csv_data(os.path.join(folder2, file))
        else:
            print(f"File {file} not found in folder2, treating as empty.")

        # Align data types between the two DataFrames
        df1, df2 = align_data_types(df1, df2)

        # Explicitly add 'Source' column, even if DataFrame is empty
        df1['Source'] = 'reportV7' if not df1.empty else 'reportV7_empty'
        df2['Source'] = 'reportV8' if not df2.empty else 'reportV8_empty'

        # Concatenate the DataFrames for comparison
        comparison_df = pd.concat([df1, df2], ignore_index=True, sort=False)

        # Add columns to show availability in each report
        comparison_df['Availability in reportV7'] = comparison_df['Source'].apply(
            lambda x: 'Available' if x == 'reportV7' else 'Unavailable'
        )
        comparison_df['Availability in reportV8'] = comparison_df['Source'].apply(
            lambda x: 'Available' if x == 'reportV8' else 'Unavailable'
        )

        # Drop the 'Source' column as it's no longer needed
        comparison_df.drop(columns=['Source'], inplace=True, errors='ignore')

        # Ensure that even if both CSVs are empty, we generate a comparison file
        output_file = os.path.join(output_folder, f'comparison_{file}')
        comparison_df.to_csv(output_file, index=False)
        print(f"Comparison report saved for {file} at {output_file}")

# Specify the paths for folder1, folder2, and the output folder
folder1 = 'ReportV7'  # Replace with the path to Folder 1
folder2 = 'ReportV8'  # Replace with the path to Folder 2
output_folder = 'comparison_output'  # Folder to save the comparison reports

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Compare CSV files and save comparison reports
compare_csv_files(folder1, folder2, output_folder)

print("Comparison completed for all common CSV files.")
