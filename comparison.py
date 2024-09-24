import os
import pandas as pd

def get_csv_files(folder):
    """Get a list of CSV files in a specified folder."""
    return [file for file in os.listdir(folder) if file.endswith('.csv')]

def read_csv_data(folder, file_name):
    """Read a CSV file and return its DataFrame, handling empty files."""
    file_path = os.path.join(folder, file_name)
    
    # Check if the file is empty before reading
    if os.path.getsize(file_path) == 0:
        print(f"Warning: The file '{file_name}' is empty.")
        return pd.DataFrame()  # Return an empty DataFrame

    df = pd.read_csv(file_path)
    
    return df

def compare_csv_files(folder1, folder2, output_folder):
    """Compare CSV files in two folders and generate individual comparison reports."""
    folder1_files = get_csv_files(folder1)
    folder2_files = get_csv_files(folder2)

    for file in folder1_files:
        if file in folder2_files:
            df1 = read_csv_data(folder1, file)
            df2 = read_csv_data(folder2, file)

            # Skip comparison if either DataFrame is empty
            if df1.empty or df2.empty:
                continue

            # Ensure the expected column exists in both DataFrames
            if 'ID' not in df1.columns or 'ID' not in df2.columns:
                print(f"Warning: The file '{file}' is missing the 'ID' column.")
                continue

            # Perform comparison and create a new DataFrame
            comparison_results = []
            for index, row in df1.iterrows():
                id_value = row['ID']
                if id_value in df2['ID'].values:
                    comparison_results.append({
                        'ID': id_value,
                        'Name': row.get('Name', 'N/A'),
                        'Value': row.get('Value', 'N/A'),
                        'Availability in reportV7': 'Available',
                        'Availability in reportV8': 'Available'
                    })
                else:
                    comparison_results.append({
                        'ID': id_value,
                        'Name': row.get('Name', 'N/A'),
                        'Value': row.get('Value', 'N/A'),
                        'Availability in reportV7': 'Available',
                        'Availability in reportV8': 'Unavailable'
                    })

            # Check for rows in df2 that are not in df1
            for index, row in df2.iterrows():
                id_value = row['ID']
                if id_value not in df1['ID'].values:
                    comparison_results.append({
                        'ID': id_value,
                        'Name': row.get('Name', 'N/A'),
                        'Value': row.get('Value', 'N/A'),
                        'Availability in reportV7': 'Unavailable',
                        'Availability in reportV8': 'Available'
                    })

            # Create a DataFrame for the comparison results
            comparison_df = pd.DataFrame(comparison_results)

            # Save the comparison report for this file
            output_file = os.path.join(output_folder, f'comparison_{file}')
            comparison_df.to_csv(output_file, index=False)
            print(f"Comparison report for {file} saved as {output_file}")

# Specify your folder paths here
folder1 = 'C:/path/to/Reportv7'  # Replace with the actual path to Folder 1
folder2 = 'C:/path/to/Reportv8'  # Replace with the actual path to Folder 2
output_folder = 'C:/path/to/output'  # Replace with the path to save comparison reports

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Compare CSV files and save individual comparison reports
compare_csv_files(folder1, folder2, output_folder)

print("Comparison completed for all common CSV files.")
