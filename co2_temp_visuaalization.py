# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style for better visuals
sns.set(style="whitegrid")

# --- Load and Clean CO₂ Emissions Data ---
co2_df = pd.read_csv("F:/LPU/Python/project 1/Co2_Emissions_by_Sectors.csv")

# Clean column names
co2_df.columns = co2_df.columns.str.strip()

# Identify Year and CO₂ emission columns
year_col_co2 = next((col for col in co2_df.columns if 'YEAR' in col.upper()), None)
co2_col = next((col for col in co2_df.columns if 'CO2_EMISSIONS' in col.upper()), None)

if not co2_col or not year_col_co2:
    raise KeyError("Couldn't find 'Year' or 'CO2 emissions' column in the CO2 dataset.")

# Aggregate CO₂ emissions by year (sum across countries/sectors)
co2_df = co2_df[[year_col_co2, co2_col]].rename(columns={year_col_co2: 'Year', co2_col: 'Global CO2 Emissions'})
co2_df = co2_df.groupby("Year", as_index=False)["Global CO2 Emissions"].sum()

# --- Load and Clean Temperature Data ---
# The dataset has multiple columns, with the first being date
temp_df = pd.read_csv("F:/LPU/Python/project 1/hadcrut-monthly-ns-avg.csv", header=None)

# First column = date, others = regional anomalies
temp_df.rename(columns={0: "Date"}, inplace=True)

# Convert non-date columns to numeric and take their row-wise mean
temp_df["Temperature_Anomaly"] = temp_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').mean(axis=1)

# Convert 'Date' to datetime and extract 'Year'
temp_df["Date"] = pd.to_datetime(temp_df["Date"], errors="coerce")
temp_df["Year"] = temp_df["Date"].dt.year

# Group by year (average temperature anomalies per year)
temp_df = temp_df.groupby("Year", as_index=False)["Temperature_Anomaly"].mean()

# --- Merge the Datasets ---
merged_df = pd.merge(co2_df, temp_df, on='Year', how='inner')

# Check for missing values
print("\nMissing values in merged dataset:")
print(merged_df.isnull().sum())

# --- Visualizations ---

# CO₂ Emissions Over Time
plt.figure(figsize=(10, 5))
sns.lineplot(data=merged_df, x='Year', y='Global CO2 Emissions', color='green')
plt.title('Global CO₂ Emissions Over Time')
plt.xlabel('Year')
plt.ylabel('CO₂ Emissions (Million Tonnes)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Temperature Anomalies Over Time
plt.figure(figsize=(10, 5))
sns.lineplot(data=merged_df, x='Year', y='Temperature_Anomaly', color='red')
plt.title('Global Temperature Anomalies Over Time')
plt.xlabel('Year')
plt.ylabel('Temperature Anomaly (°C)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Dual Axis Plot - CO₂ vs Temperature
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.set_xlabel('Year')
ax1.set_ylabel('CO₂ Emissions (Million Tonnes)', color='green')
ax1.plot(merged_df['Year'], merged_df['Global CO2 Emissions'], color='green')
ax1.tick_params(axis='y', labelcolor='green')

ax2 = ax1.twinx()
ax2.set_ylabel('Temperature Anomaly (°C)', color='red')
ax2.plot(merged_df['Year'], merged_df['Temperature_Anomaly'], color='red')
ax2.tick_params(axis='y', labelcolor='red')

plt.title('CO₂ Emissions vs Temperature Anomaly')
fig.tight_layout()
plt.grid(True)
plt.show()

# --- Summary Insights ---
print("\nInsights:")
print("- CO₂ emissions have shown a consistent upward trend since the mid-20th century.")
print("- Temperature anomalies also show a rising pattern, especially after 1980.")
print("- The dual-axis plot suggests a potential correlation between rising emissions and global warming.")
