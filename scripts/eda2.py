import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
# ../docs/EDA/
df = pd.read_csv('../datasets/merged_data_for_eda.csv')
# Define the variables for clarity
X_VAR = 'yearly_total_rainfall'
Y_VAR = 'Yield (tonnes/hectare)'
HUE_VAR = 'Country'

# 1. Create the Scatter Plot
plt.figure(figsize=(12, 7))

# Use seaborn scatterplot for visualization, colored by country
# The hue automatically addresses the DIM_Country requirement
sns.scatterplot(
    x=X_VAR,
    y=Y_VAR,
    data=df,
    hue=HUE_VAR,
    style=HUE_VAR,
    s=100, # size of points
    palette='deep'
)

# 2. Add a general trend line (regression line) for the entire dataset
# This helps assess the overall correlation across all countries.
sns.regplot(
    x=X_VAR,
    y=Y_VAR,
    data=df,
    scatter=False, # We already plotted the scatter points
    color='gray',
    line_kws={'linestyle': '--', 'alpha': 0.7}
)

# 3. Add Titles and Labels
plt.title('Relationship between Total Yearly Rainfall and Cocoa Yield (by Country)', fontsize=14)
plt.xlabel('Yearly Total Rainfall (mm)', fontsize=12)
plt.ylabel('Cocoa Yield (tonnes/hectare)', fontsize=12)

# Move legend outside the plot for better visibility
plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

# Save the plot
plt.savefig('../docs/EDA/rainfall_vs_yield_scatter.png')
plt.close()


