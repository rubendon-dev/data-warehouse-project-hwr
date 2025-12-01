import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../datasets/price/raw/Daily_price.csv')
output_filename = '../datasets/price/clean/price_by_country_year.csv'
df_target = pd.read_csv('../datasets/price/clean/price_by_country_year.csv')
# --- 1. Read the raw data of daily price ---


# --- 2. Extract and Clean the ICCO daily price (US$/tonne) ---
df = df[['Date', 'ICCO daily price (US$/tonne)']].copy()

# Column names for processing
price_column_old = 'ICCO daily price (US$/tonne)'
price_column_new = 'ICCO daily price (US$/kg)'

# Remove commas and convert to float
df[price_column_old] = (
    df[price_column_old]
    .str.replace(',', '', regex=False)
    .astype(float)
)

# Convert 'Date' to datetime and set as index
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
df.set_index('Date', inplace=True)

# --- 3. Aggregate daily data into annual, and calculate the avg for that year ---
annual_avg_df = df.resample('YE').mean()

# Convert units: US$/tonne to US$/kg (divide by 1000)
annual_avg_df[price_column_new] = annual_avg_df[price_column_old] / 1000
annual_avg_df = annual_avg_df.drop(columns=[price_column_old])

# Rename the index for clarity
annual_avg_df.index.name = 'Year'

# --- 4. Plot the annual price for each year ---
plt.figure(figsize=(12, 6))
plt.plot(annual_avg_df.index, annual_avg_df[price_column_new], marker='o', linestyle='-')

plt.title('Annual Average ICCO Price (US$/kg)', fontsize=16)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Price (US$/kg)', fontsize=12)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --- 5. Save the annual price data into the price_by_country_year file ---



# B. Prepare the annual_avg_df for merging
df_icco_final = annual_avg_df.reset_index()

# Extract the year number
df_icco_final['refYear'] = df_icco_final['Year'].dt.year

# Rename the price column to match df_target ('Avg_Price_Per_Unit')
df_icco_final = df_icco_final.rename(columns={price_column_new: 'Avg_Price_Per_Unit'})

# Add the 'partnerDesc' column and set the row name
df_icco_final['partnerDesc'] = 'World Avg ICCO'

# Select final columns to match df_target structure
df_icco_final = df_icco_final[['refYear', 'partnerDesc', 'Avg_Price_Per_Unit']]

# C. Concatenate the data
# Filter out previous 'World Avg ICCO' entries before concatenating to avoid duplicates
df_target_filtered = df_target[df_target['partnerDesc'] != 'World Avg ICCO']
df_merged = pd.concat([df_target_filtered, df_icco_final], ignore_index=True)


# D. Save the result back to the original file
df_merged.to_csv(output_filename, index=False)
def sort (output_file):
    # --- 1. Read and Sort Data by Year ---
    dff = pd.read_csv(output_file)

    # Sort the data by refYear
    df_sorted = dff.sort_values(by='refYear')

    # Save the sorted data back to the file
    df_sorted.to_csv(output_file, index=False)
    return df_sorted




def plot_country_vs_world_avg(df: pd.DataFrame):
    """
    Generates a combined bar and line chart using matplotlib to visualize
    individual country prices against the overall World Avg ICCO price trend.
    The plot is displayed using plt.show().

    Args:
        df (pd.DataFrame): DataFrame containing the merged price data.
                           Expected columns: ['refYear', 'partnerDesc', 'Avg_Price_Per_Unit'].
    """
    # Separate data
    df_countries = df[df['partnerDesc'] != 'World Avg ICCO'].copy()
    df_world_avg = df[df['partnerDesc'] == 'World Avg ICCO'].copy()

    # Sort and pivot the country data for easier grouped bar plotting in matplotlib
    # Pivot to get years as index and countries as columns
    df_pivot = df_countries.pivot_table(
        index='refYear',
        columns='partnerDesc',
        values='Avg_Price_Per_Unit'
    )

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # --- 1. Bar Chart for Individual Countries ---
    # Plot bars on the primary axis (ax1)
    df_pivot.plot(kind='bar', ax=ax1, width=0.8)

    # Set labels and rotation for the bar chart
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Country Price (US$/kg)', fontsize=12, color='C0')
    ax1.tick_params(axis='y', labelcolor='C0')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # --- 2. Line Chart for World Average (Overlaid) ---
    # Use a secondary axis (ax2) for the line plot. Although units are the same,
    # this helps manage distinct colors and separate legend entries easily.
    ax2 = ax1.twinx()

    # Ensure the world avg data is correctly indexed by refYear for plotting
    df_world_avg = df_world_avg.set_index('refYear').sort_index()

    # Plot the line on the secondary axis
    # Convert index to string for alignment with the categorical X-axis of the bars
    line, = ax2.plot(
        df_world_avg.index.astype(str),
        df_world_avg['Avg_Price_Per_Unit'],
        color='red',
        marker='o',
        linestyle='-',
        linewidth=2,
        label='World Avg ICCO Price'
    )

    # Set the same y-limits for the secondary axis to ensure visual comparison is accurate
    ax2.set_ylim(ax1.get_ylim())

    # Hide the second y-axis labels as they duplicate the first
    ax2.set_ylabel('')
    ax2.tick_params(axis='y', labelsize=0)

    # --- Final Touches ---
    ax1.set_title('Country Price Comparison with World Average ICCO Price', fontsize=16)

    # Combine legends from both plots (bars and line)
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', bbox_to_anchor=(1.05, 1))

    # Remove the ax1 legend which is now redundant with the combined one
    ax1.get_legend().remove()

    plt.tight_layout(rect=[0, 0, 1.0, 1])  # Adjust layout to make room for legend

    # Display the plot
    plt.show()

plot_country_vs_world_avg(sort(output_filename))