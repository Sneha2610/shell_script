import os
import pandas as pd

def get_csv_files(folder):
    """Get a list of CSV files in a specified folder."""
    csv_files = [file for file in os.listdir(folder) if file.endswith('.csv')]
    print(f"CSV files found in {folder}: {csv_files}")
    return csv_files

def read_csv_data(file_path):
    """Read a CSV file and return its DataFrame, handling empty files."""
    if os.path.getsize(file_path) == 0:
        print(f"Warning: The file '{file_path}' is empty.")
        return pd.DataFrame()  # Return an empty DataFrame
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

    for file in folder1_files:
        if file in folder2_files:
            df1 = read_csv_data(os.path.join(folder1, file))
            df2 = read_csv_data(os.path.join(folder2, file))

            if df1.empty or df2.empty:
                print(f"Skipping comparison for {file} due to empty data.")
                continue

            # Align data types between the two DataFrames
            df1, df2 = align_data_types(df1, df2)

            # Concatenate the DataFrames for comparison, adding an identifier column for each source
            df1['Source'] = 'reportV7'
            df2['Source'] = 'reportV8'
            comparison_df = pd.concat([df1, df2])

            # Add the Availability columns based on the source
            comparison_df['Availability in reportV7'] = comparison_df['Source'].apply(
                lambda x: 'Available' if x == 'reportV7' else 'Unavailable'
            )
            comparison_df['Availability in reportV8'] = comparison_df['Source'].apply(
                lambda x: 'Available' if x == 'reportV8' else 'Unavailable'
            )

            # Drop the 'Source' column as it's no longer needed
            comparison_df.drop(columns=['Source'], inplace=True)

            # Save the comparison result
            output_file = os.path.join(output_folder, f'comparison_{file}')
            comparison_df.to_csv(output_file, index=False)
            print(f"Comparison report saved for {file} at {output_file}")
        else:
            print(f"File {file} found in folder1 but not in folder2.")

# Specify the paths for folder1, folder2, and the output folder
folder1 = 'ReportV7'  # Replace with the path to Folder 1
folder2 = 'ReportV8'  # Replace with the path to Folder 2
output_folder = 'comparison_output'  # Folder to save the comparison reports

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Compare CSV files and save comparison reports
compare_csv_files(folder1, folder2, output_folder)

print("Comparison completed for all common CSV files.")
