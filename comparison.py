import os
import pandas as pd

def check_folders(folder1, folder2):
    """Check if the specified folders exist."""
    if not os.path.exists(folder1):
        print(f"Folder not found: {folder1}")
    if not os.path.exists(folder2):
        print(f"Folder not found: {folder2}")

def get_csv_files(folder):
    """Get a list of CSV files in a specified folder."""
    files = [file for file in os.listdir(folder) if file.endswith('.csv')]
    if not files:
        print(f"No CSV files found in {folder}.")
    return files

def read_csv_data(folder, file_name):
    """Read a CSV file and return its DataFrame, handling empty files."""
    file_path = os.path.join(folder, file_name)
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            print(f"Warning: The file '{file_name}' is empty.")
        return df
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{file_name}' is empty or cannot be read.")
        return pd.DataFrame()  # Return an empty DataFrame
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' not found.")
        return pd.DataFrame()  # Return an empty DataFrame

def compare_csv_files(folder1, folder2):
    """Compare CSV files in two folders and generate a comparison report."""
    folder1_files = get_csv_files(folder1)
    folder2_files = get_csv_files(folder2)

    comparison_results = []

    for file in folder1_files:
        if file in folder2_files:
            df1 = read_csv_data(folder1, file)
            df2 = read_csv_data(folder2, file)

            if df1.empty or df2.empty:
                continue  # Skip comparison if either DataFrame is empty

            # Perform comparison based on 'ID' or other unique identifier
            for index, row in df1.iterrows():
                id_value = row['ID']
                comparison_row = {'ID': id_value, 'Name': row['Name'], 'Value': row['Value']}

                if id_value in df2['ID'].values:
                    comparison_row['Availability in reportV7'] = 'Available'
                    comparison_row['Availability in reportV8'] = 'Available'
                else:
                    comparison_row['Availability in reportV7'] = 'Available'
                    comparison_row['Availability in reportV8'] = 'Unavailable'

                comparison_results.append(comparison_row)

            # Check for rows in df2 that are not in df1
            for index, row in df2.iterrows():
                id_value = row['ID']
                if id_value not in df1['ID'].values:
                    comparison_row = {'ID': id_value, 'Name': row['Name'], 'Value': row['Value']}
                    comparison_row['Availability in reportV7'] = 'Unavailable'
                    comparison_row['Availability in reportV8'] = 'Available'
                    comparison_results.append(comparison_row)

    # Create a DataFrame for the comparison results
    comparison_df = pd.DataFrame(comparison_results)
    return comparison_df

def save_comparison_report(comparison_df, output_file):
    """Save the comparison report to a CSV file."""
    comparison_df.to_csv(output_file, index=False)

# Specify your folder paths here
folder1 = 'C:/path/to/folder1'  # Replace with the path to Folder 1
folder2 = 'C:/path/to/folder2'  # Replace with the path to Folder 2

# Check if folders exist
check_folders(folder1, folder2)

# Compare CSV files and save the report if folders are valid
if os.path.exists(folder1) and os.path.exists(folder2):
    comparison_df = compare_csv_files(folder1, folder2)
    save_comparison_report(comparison_df, 'comparison_report.csv')
