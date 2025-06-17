import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- Configuration ---
# IMPORTANT: Ensure 'heatmap_data.json' is in the same directory as this script.
# If not, provide the full path to your heatmap_data.json file.
JSON_FILE_PATH = 'heatmap_data.json'
OUTPUT_PLOTS_DIR = 'analysis_plots' # Directory to save generated plots

# Create the output directory if it doesn't exist
if not os.path.exists(OUTPUT_PLOTS_DIR):
    os.makedirs(OUTPUT_PLOTS_DIR)


print("--- Starting Data Loading and Preparation ---")
try:
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Successfully loaded {len(df)} records from {JSON_FILE_PATH}")
except FileNotFoundError:
    print(f"Error: JSON file not found at {JSON_FILE_PATH}. Please ensure it's in the same directory.")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {JSON_FILE_PATH}. Check file format.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred during file loading: {e}")
    exit()


df['window_start'] = pd.to_datetime(df['window_start'])
df['window_end'] = pd.to_datetime(df['window_end'])

# Calculate average trade size (Total Quantity / Number of Trades)
# This metric is crucial for distinguishing characteristics of dark pools (larger block trades)
# Handle potential division by zero if 'num_trades' is 0
df['avg_trade_size'] = df.apply(
    lambda row: row['total_quantity'] / row['num_trades'] if row['num_trades'] > 0 else 0,
    axis=1
)


print("\nDataFrame Information:")
df.info()
print("\nFirst 5 rows of prepared data (including calculated avg_trade_size):")
print(df.head().to_markdown(index=False, numalign="left", stralign="left"))
print("--- Data Loading and Preparation Complete ---")


# Aggregate total trade value, quantity, and number of trades across all symbols
# and all time windows, grouped by venue.
print("\n--- Analyzing Overall Liquidity by Venue ---")
overall_liquidity_by_venue = df.groupby('venue').agg(
    total_value_overall=('total_trade_value', 'sum'),
    total_quantity_overall=('total_quantity', 'sum'),
    total_trades_overall=('num_trades', 'sum')
).reset_index().sort_values(by='total_value_overall', ascending=False)

# Plotting Overall Total Trade Value by Venue
plt.figure(figsize=(10, 6))
sns.barplot(x='venue', y='total_value_overall', data=overall_liquidity_by_venue, palette='viridis')
plt.title('Overall Total Trade Value by Venue', fontsize=16)
plt.xlabel('Trading Venue', fontsize=12)
plt.ylabel('Total Trade Value (Billions $)', fontsize=12)
plt.ticklabel_format(style='plain', axis='y') # Disable scientific notation on Y-axis
# Custom Y-axis formatter to show values in Billions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e9:.2f}B'))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout() # Adjust plot to prevent labels from overlapping
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'overall_liquidity_by_venue.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()

# Plotting Overall Total Quantity by Venue
plt.figure(figsize=(10, 6))
sns.barplot(x='venue', y='total_quantity_overall', data=overall_liquidity_by_venue, palette='plasma')
plt.title('Overall Total Quantity by Venue', fontsize=16)
plt.xlabel('Trading Venue', fontsize=12)
plt.ylabel('Total Quantity (Millions of Shares)', fontsize=12)
plt.ticklabel_format(style='plain', axis='y')
# Custom Y-axis formatter to show values in Millions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'overall_quantity_by_venue.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()

# --- 3. Dominant Symbols Analysis ---
# Aggregate total trade value and quantity per symbol across all venues and time windows.
print("\n--- Analyzing Dominant Symbols ---")
symbol_liquidity = df.groupby('symbol').agg(
    total_value_symbol=('total_trade_value', 'sum'),
    total_quantity_symbol=('total_quantity', 'sum')
).reset_index().sort_values(by='total_value_symbol', ascending=False)

# Plotting Overall Total Trade Value by Symbol
plt.figure(figsize=(10, 6))
sns.barplot(x='symbol', y='total_value_symbol', data=symbol_liquidity, palette='cividis')
plt.title('Overall Total Trade Value by Symbol', fontsize=16)
plt.xlabel('Stock Symbol', fontsize=12)
plt.ylabel('Total Trade Value (Billions $)', fontsize=12)
plt.ticklabel_format(style='plain', axis='y')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e9:.2f}B'))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'overall_liquidity_by_symbol.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()


# This plot shows how total trade value for each symbol and venue evolves over time.
# It can reveal patterns like opening/closing auction activity or intra-day shifts.
print("\n--- Analyzing Time-Series Liquidity Trends ---")
plt.figure(figsize=(16, 8)) # Larger figure for better readability of time-series
sns.lineplot(x='window_start', y='total_trade_value', hue='venue', style='symbol',
             data=df, marker='o', errorbar=None, palette='tab10', linewidth=1.5)
plt.title('Total Trade Value Over Time by Venue and Symbol', fontsize=18)
plt.xlabel('Time Window Start', fontsize=14)
plt.ylabel('Total Trade Value ($)', fontsize=14)
plt.ticklabel_format(style='plain', axis='y')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M')) # Format to Millions
plt.xticks(rotation=45, ha='right', fontsize=10) # Rotate x-axis labels for readability
plt.yticks(fontsize=10)
plt.legend(title='Venue/Symbol', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'time_series_liquidity.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()


# This is a critical analysis for dark pools, as they often facilitate larger block trades.
# Box plots are great for showing the distribution (median, quartiles, outliers) of trade sizes.
print("\n--- Analyzing Average Trade Size Distribution ---")
plt.figure(figsize=(12, 7))
# Use hue='symbol' to compare trade size characteristics per stock across venues
sns.boxplot(x='venue', y='avg_trade_size', hue='symbol', data=df, palette='Set2')
plt.title('Distribution of Average Trade Size by Venue and Symbol', fontsize=16)
plt.xlabel('Trading Venue', fontsize=12)
plt.ylabel('Average Trade Size (Shares)', fontsize=12)
plt.yscale('log') # Log scale is often useful for trade sizes due to wide ranges
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='Symbol', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'avg_trade_size_boxplot.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()

# This visualizes the split of liquidity between dark pools and lit exchanges over time.
# We'll create a stacked area plot to show the proportion.
print("\n--- Comparing Dark Pool vs. Lit Exchange Liquidity Over Time ---")
df['pool_type'] = df['venue'].apply(lambda x: 'Dark Pool' if 'DARK' in x else 'Lit Exchange')

# Aggregate total trade value by time window and pool type
time_pool_agg = df.groupby(['window_start', 'pool_type']).agg(
    sum_total_value=('total_trade_value', 'sum')
).reset_index()

plt.figure(figsize=(16, 8))
# Use seaborn.lineplot with 'stack=True' to achieve a stacked area effect
sns.lineplot(x='window_start', y='sum_total_value', hue='pool_type',
             data=time_pool_agg, marker='o', linewidth=2, errorbar=None,
             palette={'Dark Pool': '#845EC2', 'Lit Exchange': '#FFC72C'}) # Custom colors
plt.fill_between(time_pool_agg['window_start'], time_pool_agg['sum_total_value'], alpha=0.3,
                 color='#845EC2' if 'Dark Pool' in time_pool_agg['pool_type'].unique() else '#FFC72C',
                 where=time_pool_agg['pool_type'] == 'Dark Pool', interpolate=True) # Fill for dark pool
plt.fill_between(time_pool_agg['window_start'], time_pool_agg['sum_total_value'], alpha=0.3,
                 color='#FFC72C' if 'Lit Exchange' in time_pool_agg['pool_type'].unique() else '#845EC2',
                 where=time_pool_agg['pool_type'] == 'Lit Exchange', interpolate=True) # Fill for lit exchange

plt.title('Total Trade Value: Dark Pool vs. Lit Exchange Over Time', fontsize=18)
plt.xlabel('Time Window Start', fontsize=14)
plt.ylabel('Total Trade Value (Millions $)', fontsize=14)
plt.ticklabel_format(style='plain', axis='y')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
plt.legend(title='Pool Type', loc='upper left', bbox_to_anchor=(1.05, 1))
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'dark_vs_lit_time_series.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()


# This mimics KeplerGL's core map visualization, showing liquidity hotspots on abstract coordinates.
print("\n--- Generating Static Liquidity Heatmap Snapshot ---")
plt.figure(figsize=(12, 10))
# Using scatter plot where point size and color are mapped to total_trade_value
# We'll sample the data if it's too large for a clearer plot, or plot all if small.
num_sample = min(5000, len(df)) 
sampled_df = df.sample(n=num_sample, random_state=42).copy() # 

scatter = sns.scatterplot(
    x='longitude',
    y='latitude',
    size='total_trade_value', 
    hue='total_trade_value',  
    sizes=(50, 2000),         
    palette='hot',           
    alpha=0.7,               
    edgecolor='black',       
    linewidth=0.5,
    data=sampled_df
)

plt.title('Dark Pool Liquidity Hotspots (Aggregated Snapshot)', fontsize=18)
plt.xlabel('Longitude', fontsize=14)
plt.ylabel('Latitude', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.6)



for venue in df['venue'].unique():
    subset = df[df['venue'] == venue]
    if not subset.empty:
        avg_lat = subset['latitude'].mean()
        avg_lon = subset['longitude'].mean()
        plt.text(avg_lon + 0.5, avg_lat + 0.5, venue,
                 fontsize=10, weight='bold', color='white',
                 bbox=dict(boxstyle="round,pad=0.3", fc='black', ec='none', alpha=0.6))


norm = plt.Normalize(sampled_df['total_trade_value'].min(), sampled_df['total_trade_value'].max())
sm = plt.cm.ScalarMappable(cmap="hot", norm=norm)
sm.set_array([]) 
cbar = plt.colorbar(sm, ax=plt.gca(), label='Total Trade Value ($)')
cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))


plt.tight_layout()
plot_path = os.path.join(OUTPUT_PLOTS_DIR, 'static_liquidity_heatmap_snapshot.png')
plt.savefig(plot_path)
print(f"Generated plot: {plot_path}")
plt.show()

print(f"\n--- Analysis Complete ---")
print(f"All generated plots are saved in the '{OUTPUT_PLOTS_DIR}' directory.")
print("Open these .png files to view the detailed visualizations.")

