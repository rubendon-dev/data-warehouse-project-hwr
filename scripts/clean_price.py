import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
FILE_PATH = '../datasets/price/raw/trade_data_1991-2024.csv'
OUTPUT_FILE_PATH = '../datasets/price/clean/price_by_country_year.csv'


def clean_trade_data_v2(df: pd.DataFrame, remove_outliers: bool = False):
    """
    Cleans the trade data by applying a specific set of required cleaning steps,
    and optionally performs outlier removal.

    Args:
        df (pd.DataFrame): The input trade data DataFrame.
        remove_outliers (bool): If True, removes extreme outliers from 'valuePerUnit'
                                using the IQR method (1.5 * IQR).

    Returns:
        Optional[pd.DataFrame]: The cleaned DataFrame, or None if the input is empty.
    """
    if df.empty:
        print("Input DataFrame is empty. No cleaning performed.")
        return None

    initial_rows = len(df)
    print(f"--- Starting Clean: Initial Rows = {initial_rows} ---")

    # 1. Convert to numeric (turns non-numeric strings into NaN)
    df['valuePerUnit'] = pd.to_numeric(df['valuePerUnit'], errors='coerce')
    print("Step 1: 'valuePerUnit' converted to numeric. Non-numeric values coerced to NaN.")

    # 2. Drop all rows with missing values (NaN)
    df_cleaned = df.dropna().reset_index(drop=True)
    rows_dropped_missing = initial_rows - len(df_cleaned)
    df = df_cleaned
    print(f"Step 2: Dropped rows with missing data (NaN). Rows removed: {rows_dropped_missing}")

    # 3. Standardize 'partnerDesc' (ROBUST FIX)
    # This uses a non-greedy wildcard regex to fix the failed character match ('C矌e d\'Ivoire').
    rows_before_text_fix = len(df)
    df['partnerDesc'] = df['partnerDesc'].astype(str).apply(
        lambda x: re.sub(r'C.*?e d\'Ivoire', "Cote d'Ivoire", x, flags=re.IGNORECASE))
    print(f"Step 3: 'partnerDesc' standardized for 'Côte d\'Ivoire' variations (FIXED).")


    # 4. Outlier Treatment (Addressing the Indonesia 2003 issue)
    if remove_outliers:
        df = remove_extreme_outliers(df)

    final_rows = len(df)
    print(f"--- Clean Finished ---")
    print(f"Total Rows Removed: {initial_rows - final_rows}")
    print(f"Final Rows: {final_rows}")
    print("-" * 30)

    return df


def remove_extreme_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes extreme outliers from the 'valuePerUnit' column using the IQR method.
    The IQR method defines outliers as values outside 1.5 * IQR (Interquartile Range).
    """
    if df.empty:
        return df

    # Calculate Q1, Q3, and IQR
    Q1 = df['valuePerUnit'].quantile(0.25)
    Q3 = df['valuePerUnit'].quantile(0.75)
    IQR = Q3 - Q1

    # Define bounds for non-outliers
    multiplier = 3.0
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    rows_before_outlier_removal = len(df)

    # Filter out values outside the bounds
    df_filtered = df[
        (df['valuePerUnit'] >= lower_bound) &
        (df['valuePerUnit'] <= upper_bound)
        ]
    df_filtered = df_filtered.reset_index(drop=True)

    rows_dropped_outliers = rows_before_outlier_removal - len(df_filtered)

    print(
        f"Step 4 (Outlier Removal): Removed extreme 'valuePerUnit' outliers ({multiplier}*IQR). Rows removed: {rows_dropped_outliers}")

    return df_filtered


def calculate_average_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the average price per unit ('valuePerUnit') for each
    combination of 'refYear' and 'partnerDesc'.
    """
    if df.empty:
        return pd.DataFrame(columns=['refYear', 'partnerDesc', 'Avg_Price_Per_Unit'])

    avg_price_df = df.groupby(['refYear', 'partnerDesc'])['valuePerUnit'].mean()
    avg_price_df = avg_price_df.reset_index()
    avg_price_df.rename(columns={'valuePerUnit': 'Avg_Price_Per_Unit'}, inplace=True)

    print("--- Average Price Calculation Finished ---")
    print(f"Resulting table size: {len(avg_price_df)} rows.")
    print("-" * 30)

    return avg_price_df


def find_missing_country_years(avg_price_df: pd.DataFrame):
    """
    Identifies which (Year, Country) combinations are missing from the aggregated data
    and visualizes this missingness using a heatmap.

    This occurs when a country is present in at least one year, but not in all years
    between the min and max year of the dataset.

    Args:
        avg_price_df (pd.DataFrame): The aggregated DataFrame (Avg_Price_Per_Unit).
    """
    if avg_price_df.empty:
        print("Missing Data Check: Aggregated DataFrame is empty.")
        return

    # 1. Get all unique years and countries
    all_years = avg_price_df['refYear'].unique()
    all_countries = avg_price_df['partnerDesc'].unique()

    # 2. Create a dense grid of all possible (Year, Country) combinations
    index_year = pd.MultiIndex.from_product([all_years, all_countries], names=['refYear', 'partnerDesc'])
    complete_grid = pd.DataFrame(index=index_year).reset_index()

    # 3. Merge the complete grid with the actual data (outer join)
    merged_df = pd.merge(
        complete_grid,
        avg_price_df,
        on=['refYear', 'partnerDesc'],
        how='left'
    )

    # 4. Find the missing combinations (where Avg_Price_Per_Unit is NaN)
    missing_data = merged_df[merged_df['Avg_Price_Per_Unit'].isna()]

    print("--- Missing (Year, Country) Combinations ---")
    if missing_data.empty:
        print("Data is complete: All countries are present in all years.")
    else:
        # Text Output (for console)
        missing_by_year = missing_data.groupby('refYear')['partnerDesc'].apply(list)

        print(f"Total missing combinations: {len(missing_data)}")
        for year, countries in missing_by_year.items():
            print(f"Year {year}: Missing Countries: {', '.join(countries)}")

        # --- NEW PLOTTING LOGIC: Heatmap ---
        print("\n--- Generating Missing Data Heatmap ---")

        # Create a pivot table from the merged data. The 'Avg_Price_Per_Unit' column
        # is NaN for missing data and a value for present data.
        heatmap_data = merged_df.pivot_table(
            index='partnerDesc',
            columns='refYear',
            values='Avg_Price_Per_Unit'
        )

        # Create the missing matrix: 1 if NaN (missing), 0 if value exists (present)
        missing_matrix = heatmap_data.isna().astype(int)
        custom_cmap = ['#E0E0E0', '#8f8d8d']
        # Plot the heatmap
        plt.figure(figsize=(12, max(6, len(all_countries) * 0.5)))
        sns.heatmap(
            missing_matrix,
            cbar=False,
            cmap=custom_cmap,
            linewidths=.5,
            linecolor='lightgray',
            annot=True,  # Show 0/1 markers on the plot
            fmt='d'
        )
        plt.title('Heatmap of Missing Country Price Data by Year (1 = Missing)', fontsize=16)
        plt.xlabel('Reference Year', fontsize=12)
        plt.ylabel('Partner Country', fontsize=12)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()

        print("Heatmap of missing data created successfully.")

    print("-" * 30)


def plot_average_price(df: pd.DataFrame):
    """
    Generates a bar plot showing the average price per unit over time for all countries.
    """
    if df.empty or 'refYear' not in df.columns or 'Avg_Price_Per_Unit' not in df.columns:
        print("Cannot plot: DataFrame is empty or missing required columns ('refYear', 'Avg_Price_Per_Unit').")
        return

    sns.set_style("whitegrid")
    plt.figure(figsize=(15, 8))

    sns.barplot(
        data=df,
        x='refYear',
        y='Avg_Price_Per_Unit',
        hue='partnerDesc',
        errorbar=None
    )

    plt.title('Average Price Per Unit Over Time by Partner Country (Bar Chart)', fontsize=16)
    plt.xlabel('Reference Year', fontsize=12)
    plt.ylabel('Average Price Per Unit', fontsize=12)

    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.xticks(rotation=45, ha='right')

    plt.grid(True, linestyle='--', alpha=0.6, axis='y')
    plt.tight_layout()
    plt.show()

    print("--- Price Trend Plot Generated (Bar Chart) ---")
    print("Plot object created successfully.")
    print("-" * 30)



try:
    # 1. Read the data
    trade_df = pd.read_csv(FILE_PATH)

    # 2. Execute the clean function WITH outlier removal (True)
    # This should resolve the Indonesia 2003 issue by dropping the single extreme transaction.
    cleaned_df = clean_trade_data_v2(trade_df.copy(), remove_outliers=True)

    if cleaned_df is not None:
        # 3. Execute the calculation function
        avg_price_df = calculate_average_price(cleaned_df)

        # 4. Execute the missing data check function (NEW)
        find_missing_country_years(avg_price_df)

        # 5. Execute the plotting function
        plot_average_price(avg_price_df)

        # 6. Save the aggregated file
        avg_price_df.to_csv(OUTPUT_FILE_PATH, index=False)
        print(f"Final results saved to: {OUTPUT_FILE_PATH}")

        # 7. Check the Indonesia 2003 average price after treatment
        indonesia_2003_check = avg_price_df[
            (avg_price_df['partnerDesc'] == 'Indonesia') &
            (avg_price_df['refYear'] == 2003)
            ]
        print("\n--- Validation Check: Indonesia 2003 Price ---")
        if not indonesia_2003_check.empty:
            print(
                f"Indonesia 2003 Avg Price (after outlier removal): {indonesia_2003_check['Avg_Price_Per_Unit'].iloc[0]:.4f}")
        else:
            print("No Indonesia 2003 data remaining after cleaning.")


except FileNotFoundError:
    print(f"\nError: File not found at the expected path: {FILE_PATH}. Please ensure the file is uploaded.")
except Exception as e:
    print(f"\nAn unexpected error occurred during processing: {e}")