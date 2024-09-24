import os
import pandas as pd

def get_csv_files(folder):
    """Get a list of CSV files in a specified folder."""
    return [file for file in os.listdir(folder) if file.endswith('.csv')]

def read_csv_data(folder, file_name):
    """Read a CSV file and return its DataFrame."""
    file_path = os.path.join(folder, file_name)
    return pd.read_csv(file_path)

def compare_csv_files(folder1, folder2):
    """Compare CSV files in two folders and generate a comparison report."""
    folder1_files = get_csv_files(folder1)
    folder2_files = get_csv_files(folder2)

    comparison_results = []

    for file in folder1_files:
        if file in folder2_files:
            df1 = read_csv_data(folder1, file)
            df2 = read_csv_data(folder2, file)

            # Perform comparison
            for index, row in df1.iterrows():
                id_value = row['ID']
                if id_value in df2['ID'].values:
                    comparison_results.append({
                        'ID': id_value,
                        'Name': row['Name'],
                        'Value': row['Value'],
                        'Availability in reportV7': 'Available',
                        'Availability in reportV8': 'Available'
                    })
                else:
                    comparison_results.append({
                        'ID': id_value,
                        'Name': row['Name'],
                        'Value': row['Value'],
                        'Availability in reportV7': 'Available',
                        'Availability in reportV8': 'Unavailable'
                    })

            # Check for rows in df2 that are not in df1
            for index, row in df2.iterrows():
                id_value = row['ID']
                if id_value not in df1['ID'].values:
                    comparison_results.append({
                        'ID': id_value,
                        'Name': row['Name'],
                        'Value': row['Value'],
                        'Availability in reportV7': 'Unavailable',
                        'Availability in reportV8': 'Available'
                    })

    # Create a DataFrame for the comparison results
    comparison_df = pd.DataFrame(comparison_results)
    return comparison_df

def save_comparison_report(comparison_df, output_file):
    """Save the comparison report to a CSV file."""
    comparison_df.to_csv(output_file, index=False)

# Specify your folder paths here
folder1 = 'Reportv7'  # Replace with the path to Folder 1
folder2 = 'Reportv8'  # Replace with the path to Folder 2

# Compare CSV files and save the report
comparison_df = compare_csv_files(folder1, folder2)
save_comparison_report(comparison_df, 'comparison_report.csv')
