import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# # Load data
# try:
#     fact_df = pd.read_csv('../datasets/star_schema/Fact_table.csv')
#     country_df = pd.read_csv('../datasets/star_schema/dim_country.csv')
#     date_df = pd.read_csv('../datasets/star_schema/dim_date.csv')
#
#     # Merge dataframes
#     merged_df = fact_df.merge(country_df, on='country_id', how='left')
#     merged_df = merged_df.merge(date_df, on='date_id', how='left')
#
#     # Drop redundant ID columns and rename for clarity
#     merged_df = merged_df.drop(columns=['fact_id', 'country_id', 'date_id'])
#     merged_df = merged_df.rename(columns={'Year': 'Date'})
#
#     # Save the merged DataFrame for subsequent EDA steps
#     merged_df.to_csv('merged_data_for_eda.csv', index=False)
#
#     print("Data successfully merged and saved to 'merged_data_for_eda.csv'.")
#
# except Exception as e:
#     print(f"An error occurred during loading or merging: {e}")

df = pd.read_csv('../datasets/merged_data_for_eda.csv')

# 1. Overall Production Trend
yearly_production = df.groupby('Date')['Production (tonnes)'].sum().reset_index()

plt.figure(figsize=(10, 6))
plt.plot(yearly_production['Date'], yearly_production['Production (tonnes)'], marker='o', linestyle='-')
plt.title('Overall Annual Production Trend (Tonnes)')
plt.xlabel('Year')
plt.ylabel('Production (Tonnes)')
plt.grid(True)
plt.savefig('../docs/EDA/overall_production_trend.png')
plt.close()

# 2. Production Trend by Country
plt.figure(figsize=(12, 7))
for country in df['Country'].unique():
    country_data = df[df['Country'] == country]
    plt.plot(country_data['Date'], country_data['Production (tonnes)'], label=country, marker='.')
plt.title('Annual Production Trend by Country (Tonnes)')
plt.xlabel('Year')
plt.ylabel('Production (Tonnes)')
plt.legend(title='Country')
plt.grid(True)
plt.savefig('../docs/EDA/country_production_trend.png')
plt.close()

# Calculate total production by country and sort
country_production = df.groupby('Country')['Production (tonnes)'].sum().sort_values(ascending=False).reset_index()

# Plot: Total Production by Country
plt.figure(figsize=(10, 6))
plt.bar(country_production['Country'], country_production['Production (tonnes)'], color='skyblue')
plt.title('Total Production by Country (Tonnes)')
plt.xlabel('Country')
plt.ylabel('Total Production (Tonnes)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('../docs/EDA/total_production_by_country_bar.png')
plt.close()

# Set aesthetic style
sns.set_style("whitegrid")

# 1. Histogram of Yield
plt.figure(figsize=(10, 6))
sns.histplot(df['Yield (tonnes/hectare)'], kde=True, bins=15)
plt.title('Distribution of Yield (tonnes/hectare)')
plt.xlabel('Yield (tonnes/hectare)')
plt.ylabel('Frequency')
plt.savefig('../docs/EDA/yield_distribution_histogram.png')
plt.close()

# 2. Box Plot of Yield by Country
plt.figure(figsize=(10, 6))
sns.boxplot(x='Country', y='Yield (tonnes/hectare)', data=df)
plt.title('Yield Distribution by Country')
plt.xlabel('Country')
plt.ylabel('Yield (tonnes/hectare)')
plt.savefig('../docs/EDA/yield_distribution_boxplot.png')
plt.close()

# Plot: Scatter Plot of Avg Temperature vs. Yield
plt.figure(figsize=(10, 6))
sns.scatterplot(x='yearly_avg_temperature', y='Yield (tonnes/hectare)', data=df, hue='Country', style='Country', s=100)
plt.title('Relationship between Yearly Avg Temperature and Yield')
plt.xlabel('Yearly Average Temperature')
plt.ylabel('Yield (tonnes/hectare)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('../docs/EDA/temp_yield_scatter.png')
plt.close()


# Select only numerical columns for correlation
numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
correlation_matrix = df[numerical_cols].corr()

# Plot: Correlation Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Correlation Matrix of Numerical Variables')
plt.tight_layout()
plt.savefig('../docs/EDA/correlation_heatmap.png')
plt.close()