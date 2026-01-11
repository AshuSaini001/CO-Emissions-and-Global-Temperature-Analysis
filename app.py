import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Configuration ---
st.set_page_config(page_title="Climate Data Dashboard", layout="wide")

# Title and Description
st.title("🌍 Climate Change Analysis Dashboard")
st.markdown("""
This dashboard visualizes the correlation between **Global CO₂ Emissions** and **Temperature Anomalies**.
You can use the default data or upload updated CSV files via the sidebar.
""")

# Set Seaborn style
sns.set(style="whitegrid")

# --- Sidebar: File Uploads ---
st.sidebar.header("📂 Data Management")
st.sidebar.info("Upload updated CSV files here. If no file is uploaded, the app will use the default historical data.")

uploaded_co2_file = st.sidebar.file_uploader("Upload CO₂ Emissions CSV", type=["csv"])
uploaded_temp_file = st.sidebar.file_uploader("Upload Temperature CSV", type=["csv"])

# --- Data Loading Logic ---
def load_and_process_data():
    # 1. Load CO2 Data
    if uploaded_co2_file is not None:
        co2_df = pd.read_csv(uploaded_co2_file)
        st.sidebar.success("✅ Custom CO₂ data loaded")
    else:
        try:
            co2_df = pd.read_csv("Co2_Emissions_by_Sectors.csv")
        except FileNotFoundError:
            st.error("Default CO₂ file not found. Please upload a CSV.")
            return None, None

    # 2. Load Temperature Data
    if uploaded_temp_file is not None:
        # Check if it has a header or not (assuming standard format for uploaded updates usually has headers, 
        # but the specific hadcrut dataset often comes without. We stick to the logic of the specific dataset structure)
        # Note: If your new data has headers, you might need to adjust 'header=None'
        temp_df = pd.read_csv(uploaded_temp_file, header=None)
        st.sidebar.success("✅ Custom Temp data loaded")
    else:
        try:
            temp_df = pd.read_csv("hadcrut-monthly-ns-avg.csv", header=None)
        except FileNotFoundError:
            st.error("Default Temperature file not found. Please upload a CSV.")
            return None, None

    return co2_df, temp_df

# Load raw data
co2_raw, temp_raw = load_and_process_data()

if co2_raw is not None and temp_raw is not None:
    try:
        # --- Clean CO2 Data ---
        co2_clean = co2_raw.copy()
        co2_clean.columns = co2_clean.columns.str.strip()
        
        # Dynamic column finding
        year_col_co2 = next((col for col in co2_clean.columns if 'YEAR' in col.upper()), None)
        co2_col = next((col for col in co2_clean.columns if 'CO2_EMISSIONS' in col.upper()), None)
        
        if not year_col_co2 or not co2_col:
            st.error("Error: Could not find 'YEAR' or 'CO2_EMISSIONS' columns in the CO2 file.")
            st.stop()

        co2_clean = co2_clean[[year_col_co2, co2_col]].rename(columns={year_col_co2: 'Year', co2_col: 'Global CO2 Emissions'})
        co2_clean = co2_clean.groupby("Year", as_index=False)["Global CO2 Emissions"].sum()

        # --- Clean Temperature Data ---
        temp_clean = temp_raw.copy()
        # Ensure we treat column 0 as Date
        temp_clean.rename(columns={0: "Date"}, inplace=True)
        
        # Calculate mean of all other columns (regional data)
        temp_clean["Temperature_Anomaly"] = temp_clean.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').mean(axis=1)
        
        # Extract Year
        temp_clean["Date"] = pd.to_datetime(temp_clean["Date"], errors="coerce")
        temp_clean["Year"] = temp_clean["Date"].dt.year
        
        # Group by Year
        temp_clean = temp_clean.groupby("Year", as_index=False)["Temperature_Anomaly"].mean()

        # --- Merge Data ---
        merged_df = pd.merge(co2_clean, temp_clean, on='Year', how='inner')

        # --- Layout: Key Metrics ---
        st.subheader("📊 Key Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Start Year", merged_df['Year'].min())
        col2.metric("End Year", merged_df['Year'].max())
        col3.metric("Data Points", len(merged_df))

        # --- Layout: Charts ---
        st.markdown("---")
        
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Global CO₂ Emissions")
            fig1 = plt.figure(figsize=(6, 4))
            sns.lineplot(data=merged_df, x='Year', y='Global CO2 Emissions', color='green')
            plt.ylabel('Million Tonnes')
            plt.grid(True, alpha=0.3)
            st.pyplot(fig1)

        with col_right:
            st.subheader("Temperature Anomalies")
            fig2 = plt.figure(figsize=(6, 4))
            sns.lineplot(data=merged_df, x='Year', y='Temperature_Anomaly', color='red')
            plt.ylabel('Anomaly (°C)')
            plt.grid(True, alpha=0.3)
            st.pyplot(fig2)

        # Dual Axis Plot (Full Width)
        st.subheader("📉 Correlation Analysis: Emissions vs. Warming")
        fig3, ax1 = plt.subplots(figsize=(10, 4))
        
        ax1.set_xlabel('Year')
        ax1.set_ylabel('CO₂ Emissions', color='green')
        ax1.plot(merged_df['Year'], merged_df['Global CO2 Emissions'], color='green', linewidth=2)
        ax1.tick_params(axis='y', labelcolor='green')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Temperature Anomaly (°C)', color='red')
        ax2.plot(merged_df['Year'], merged_df['Temperature_Anomaly'], color='red', linestyle='--', linewidth=2)
        ax2.tick_params(axis='y', labelcolor='red')
        
        plt.title('Dual Axis Comparison')
        st.pyplot(fig3)

        # --- Data Preview Section ---
        with st.expander("View Raw Merged Data"):
            st.dataframe(merged_df)

    except Exception as e:
        st.error(f"An error occurred while processing the data: {e}")
        st.write("Please ensure your uploaded CSVs match the format of the original datasets.")
