import pandas as pd
import glob
import os

# Define the directory and file prefix
directory = r"C:\Users\Administrator\Downloads"
file_prefix = "export-Person-2024-09-17"
output_csv = os.path.join(directory, "combined_output.csv")

# Find all Excel files with the specified prefix
excel_files = glob.glob(os.path.join(directory, f"{file_prefix}*.xls"))

# List to hold DataFrames
dataframes = []

# Read each Excel file and append to the list
for file in excel_files:
    print(f"Processing file: {file}")
    df = pd.read_excel(file)  # Read the Excel file
    dataframes.append(df)  # Append DataFrame to the list

# Combine all DataFrames into one
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(output_csv, index=False)
    print(f"Combined CSV saved to: {output_csv}")
else:
    print("No files found with the specified prefix.")
