import pandas as pd
import os

# Define the input and output filenames
input_filename = '../datasets/TradeData_raw.csv'
output_filename = '../datasets/TradeData.csv'

# Define the columns to extract based on the names provided by the user.
columns_to_extract_names = ['period', 'partnerDesc', 'fobvalue', 'netWgt']

# Check if the output file already exists
if os.path.exists(output_filename):
    print(f"Output file '{output_filename}' already exists. Skipping data extraction.")
else:
    try:
        # Load the data, specifying the 'latin1' encoding to resolve potential UnicodeDecodeError.
        df = pd.read_csv(input_filename, index_col=False, encoding='latin1')

        # Select the specified columns
        df_extracted = df[columns_to_extract_names]

        # Save the extracted data to a new CSV file
        df_extracted.to_csv(output_filename, index=False, encoding='utf-8')

        print(f"Columns successfully extracted and saved to '{output_filename}'.")

    except FileNotFoundError:
        print(f"Error: The input file '{input_filename}' was not found.")
    except KeyError as e:
        print(f"Error: One or more specified columns were not found in the file: {e}")

