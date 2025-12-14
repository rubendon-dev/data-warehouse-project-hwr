import pandas as pd
import glob
import os

# --- Configuration ---
# Search pattern for all raw files (e.g., *_raw.csv)
RAW_FILE_PATTERN = '*_raw.csv'
OUTPUT_DIR = 'cleaned_yearly_data'

# Create the output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Core Processing Function ---

def clean_and_aggregate_data(file_path):
    """
    Reads a raw climate CSV file, performs essential cleaning steps (header fix, 
    type conversion), and aggregates the daily data into yearly statistics.
    """
    
    file_name = os.path.basename(file_path)
    print(f"Processing: {file_name}")

    # 1. CLEANING: Correctly read the file by skipping initial metadata rows.
    try:
        # Use header=1 to get the column names into the second row of the file.
        df_raw = pd.read_csv(file_path, header=1)
    except Exception as e:
        print(f"ERROR reading {file_name}: {e}")
        return None

    # Get the correct column names from the first row (index 0) of the current DataFrame.
    new_columns = df_raw.iloc[0].tolist()
    
    # The actual data starts from the third row (index 1 of the current DataFrame).
    df_data = df_raw.iloc[1:].copy()
    df_data.columns = new_columns

    # Remove columns that contain only metadata and NaNs (e.g., 'utc_offset_seconds').
    df_data = df_data.dropna(axis=1, how='all')

    # Rename columns to remove units for easier use in calculations
    df_data = df_data.rename(columns={
        'time': 'time',
        'temperature_2m_mean (°C)': 'temperature_2m_mean',
        'rain_sum (mm)': 'rain_sum'
    })
    
    # Convert the 'time' column to datetime objects
    df_data['time'] = pd.to_datetime(df_data['time'])

    # Convert the numerical columns to float. Errors are coerced to NaN (though none expected).
    cols_to_convert = ['temperature_2m_mean', 'rain_sum']
    for col in cols_to_convert:
        df_data[col] = pd.to_numeric(df_data[col], errors='coerce')


    # 2. TRANSFORMATION (Aggregation - Logic from your original file)
    
    # Extract the year from the datetime object
    df_data['year'] = df_data['time'].dt.year

    # Group by year and calculate the required yearly statistics
    df_yearly = df_data.groupby('year').agg(
        # Temperature statistics
        temperature_mean_yearly=('temperature_2m_mean', 'mean'),
        temperature_min_yearly=('temperature_2m_mean', 'min'),
        temperature_max_yearly=('temperature_2m_mean', 'max'),
        
        # Rainfall statistics
        rain_sum_yearly=('rain_sum', 'sum'),
        rain_mean_yearly=('rain_sum', 'mean'),
        rain_min_yearly=('rain_sum', 'min'),
        rain_max_yearly=('rain_sum', 'max')
    ).reset_index()

    return df_yearly

# --- Main Execution ---

def main():
    """
    Main function to run the process for all raw climate files found in the directory.
    """
    # Find all raw files in the current directory
    raw_files = glob.glob(RAW_FILE_PATTERN)
    
    if not raw_files:
        print(f"ERROR: No files matching the pattern '{RAW_FILE_PATTERN}' found.")
        print("Please ensure the script is in the same folder as your raw CSV files.")
        return

    print(f"Found {len(raw_files)} raw files to process.")
    
    # Process each file
    for file_path in raw_files:
        df_yearly = clean_and_aggregate_data(file_path)
        
        if df_yearly is not None:
            # Create the output filename (e.g., 'climate_data_brazil_raw.csv' -> 'yearly_climate_data_brazil.csv')
            base_name = os.path.basename(file_path)
            country_name = base_name.replace('_raw.csv', '').replace('climate_data_', '')
            output_file_name = os.path.join(OUTPUT_DIR, f'yearly_climate_data_{country_name}.csv')
            
            # Save the final, clean, and aggregated file
            df_yearly.to_csv(output_file_name, index=False)
            print(f"Successfully saved clean data to: {output_file_name}")
            
    print("\n--- Processing Complete ---")
    print(f"All yearly files are saved in the '{OUTPUT_DIR}' folder.")


if __name__ == "__main__":
    main()