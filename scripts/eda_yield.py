import pandas as pd

# Define the file paths
YIELD_FILE = '../datasets/cocoa-bean-yields.csv'
PRODUCTION_FILE = '../datasets/cocoa-beans-production-by-region.csv'

def analyze_cocoa_data(file_path, original_col_name, new_col_name, analysis_type):
    """
    Performs yield or production analysis (max and top 10 average) for cocoa data.
    """
    print(f"\n==============================================")
    print(f"ANALYSIS: {analysis_type}")
    print(f"==============================================")

    # 1. Load the data
    df = pd.read_csv(file_path)

    # 2. Clean up the column name
    df.rename(columns={original_col_name: new_col_name}, inplace=True)

    # 3. Filter out regional aggregates (where 'Code' is missing) to focus on countries
    df_countries = df.dropna(subset=['Code'])

    # 4. Calculate Maximum Record per Entity (Country)
    max_record_country = (
        df_countries.groupby('Entity')[new_col_name]
        .max()
        .sort_values(ascending=False)
        .head(1)
    )
    print(f"\n--- Entity with the Single Highest Recorded {analysis_type} (Maximum) ---")
    print(max_record_country) # Outputting directly from code for exact numbers


    # 5. Calculate Average Record per Entity (Country).
    avg_record_by_country = df_countries.groupby('Entity')[new_col_name].mean()

    # 6. Find Top 10 Countries by Average Record.
    top_10_countries = avg_record_by_country.sort_values(ascending=False).head(10)
    print(f"\n--- Top 10 Entities by Average Annual {analysis_type} (Mean) ---")
    print(top_10_countries) # Outputting directly from code for exact numbers


# --- Execution ---

# A. Analysis for Yield Data
analyze_cocoa_data(
    file_path=YIELD_FILE,
    original_col_name='Cocoa beans | 00000661 || Yield | 005412 || tonnes per hectare',
    new_col_name='Yield (tonnes per hectare)',
    analysis_type='Yield'
)

# B. Analysis for Production Data
analyze_cocoa_data(
    file_path=PRODUCTION_FILE,
    original_col_name='Cocoa beans | 00000661 || Production | 005510 || tonnes',
    new_col_name='Production (tonnes)',
    analysis_type='Production'
)