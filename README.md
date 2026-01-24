# 🍫 Cocoa Data Warehouse Project
A robust ETL pipeline and Star Schema design for analyzing global cocoa market trends. A project by Daphne, Christopher and Ruben.

## Project Overview
This project integrates structured data from the ICCO, UN Comtrade, and ECMWF to analyze the correlation between climate patterns, production yields, and global cocoa prices. We utilize a traditional ETL pipeline to transform raw, daily records into a standardized Star Schema with annual granularity.

## Project Structure
```
data-warehouse-project-hwr/
├── datasets/                            # Datasets used, categorized by climate,price, production.
│   ├── climate/                          
│   ├── price/                            
│   ├── production/
│   ├── star_schema/                     # Final star_schema 
│   ├── merged_data_for_eda.csv          # merged data for plotting
├── docs/                         
│   ├── EDA                              # Initial EDA results
├── scripts/                             # python scripts for ETL
│   ├── clean_and_aggregate_climate.py                                               
│   ├── clean_price.py  
│   ├── combine_price_sources.py
│   ├── extract_trade_data.py
│   ├── merged_data_eda.py                         
├── README.md                            # Project overview 
```

## Tech Stack
- Language: Python (Pandas, NumPy)
- Visuals: Seaborn & Matplotlib (for EDA), Tableau (for final Dashboards)
- Architecture: Star Schema (Dimensional Modeling)
- ETL Tool: KNIME / Python Scripts
