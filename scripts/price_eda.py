import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the data
tradeData_file_path = '../datasets/tradeData.csv'
monthlyPrice_file_path = '../datasets/Monthly_Average_Price.csv'

def basic_eda(file_path):
    df = pd.read_csv(file_path)
    # 1. Display the first 5 rows
    print("## 1. Data Head (First 5 Rows)")
    print(df.head().to_markdown(index=False))
    print("\n" + "=" * 50 + "\n")

    # 2. Display column information, data types, and non-null counts
    print("## 2. Data Information and Types")
    df.info()
    print("\n" + "="*50 + "\n")

    # 3. Display descriptive statistics for numerical columns
    print("## 3. Descriptive Statistics (Numerical Columns)")
    # Using .T to transpose for better readability
    print(df.describe().T.to_markdown())
    print("\n" + "="*50 + "\n")

    # 4. Check for missing values
    print("## 4. Missing Values Count")
    missing_values = df.isnull().sum()
    print(missing_values.to_markdown(numalign="left", stralign="left"))
    print("\n" + "="*50 + "\n")



def avg_unit_value(file_path):
    df = pd.read_csv(file_path)
    avg_trade_data = df.groupby(['period', 'partnerDesc'])[['netWgt', 'fobvalue']].mean().reset_index()
    avg_trade_data['avg_fobvalue_per_netwgt'] = avg_trade_data['fobvalue'] / avg_trade_data['netWgt']
    print("--- Average Net Weight and FOB Value per Country and Year ---\n")
    print(avg_trade_data.to_markdown(index=False, floatfmt=(".0f", ".2f")))
    return avg_trade_data


def plot(plot_data):
    # Get years and countries
    years = plot_data.index.astype(str)
    countries = plot_data.columns
    num_countries = len(countries)
    # --- Grouped Bar Chart Plotting ---

    # Setup plotting parameters
    bar_width = 0.8 / num_countries  # Determine the width of each bar
    r = np.arange(len(years))  # Set of base positions for groups (one position per year)

    plt.figure(figsize=(15, 8))

    # Plot bars for each country
    for i, country in enumerate(countries):
        # Calculate the position for the current country's bars
        # This shifts the bar group by half the total bar width to center it,
        # then shifts it by the current bar index * bar_width
        bar_pos = r + i * bar_width - (num_countries * bar_width) / 2 + bar_width / 2

        # Plot the data
        plt.bar(bar_pos, plot_data[country].values, width=bar_width, label=country)

    # Customize the chart
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Avg FOB Value per Net Weight (Price per Unit Weight)', fontsize=12)
    plt.title('Average FOB Value per Net Weight by Country and Year', fontsize=14)

    # Set x-axis ticks to be the years and center them
    plt.xticks(r, years, rotation=45, ha='right')

    # Add legend outside the plot area
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust layout to make room for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

def plot_price(input_filename):
    # 1. Load the data, handling the thousands separator (',') found in the price columns
    df = pd.read_csv(input_filename, thousands=',')

    # 2. Clean the column names by removing quotes and trimming whitespace
    df.columns = df.columns.str.replace('"', '').str.strip()

    # 3. Convert 'Month' column to datetime objects
    # Assuming the format is Day/Month/Year (DD/MM/YYYY) based on the file snippet
    df['Month'] = pd.to_datetime(df['Month'], format='%d/%m/%Y', errors='coerce')

    # 4. Ensure price columns are numeric (float)
    price_cols = ['Euro/tonne', 'US$/tonne']
    for col in price_cols:
        # Since we used thousands=',' in read_csv, this primarily ensures type consistency
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 5. Drop any rows where 'Month' is missing after conversion (if errors='coerce' was triggered)
    df.dropna(subset=['Month'], inplace=True)

    # 6. Sort the data by date for correct line plot
    df = df.sort_values('Month')

    # --- Line Chart Plotting ---

    plt.figure(figsize=(12, 6))

    # Plot the price trends
    plt.plot(df['Month'], df['Euro/tonne'], label='Euro/tonne', marker='.', linestyle='-', markersize=3)
    plt.plot(df['Month'], df['US$/tonne'], label='US$/tonne', marker='.', linestyle='-', markersize=3)

    # Customize the chart
    plt.title('Monthly Average Price Trend (Euro and US Dollar per Tonne)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price per Tonne', fontsize=12)

    # Format the X-axis for better date readability
    # Use MajorLocator for annual ticks and DateFormatter for 'Year-Month' display
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))  # Show major ticks every 2 years for clarity

    plt.xticks(rotation=45, ha='right')

    plt.legend(title='Currency')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

#execute
# basic_eda(tradeData_file_path)
plot_data = avg_unit_value(tradeData_file_path).pivot(index='period', columns='partnerDesc', values='avg_fobvalue_per_netwgt')
plot(plot_data)

basic_eda(monthlyPrice_file_path)
# plot_price(monthlyPrice_file_path)