import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest

# Page settings
st.set_page_config(page_title="Cross-Chain Token Tracker", layout="wide")

st.title("🔗 Cross-Chain Token Tracker")
st.markdown("Visualize recent **USDT token transfers** across Ethereum, BNB, and Polygon.")

st.info("""
This dashboard shows recent **USDT token transfers** across Ethereum, BNB, and Polygon chains.

- Choose a chain from the sidebar  
- Filter transfers by wallet address  
- View total volume, number of transfers, and per-block activity  
- Detect abnormal transfers using anomaly detection
""")



# Chain selector
chain = st.sidebar.selectbox("Choose a chain", ["eth", "polygon", "bnb"])
wallet_filter = st.sidebar.text_input("Filter by wallet address (optional)").lower()

# Map chain to file
file_path = f"data/{chain}_transfers.csv"
if st.button("🔁 Refresh Data Now"):
    with st.spinner("Fetching new data..."):
        import subprocess
        result = subprocess.run(
            ["python", "scripts/alt_fetch_token.py"],
            capture_output=True,
            text=True
        )
    if result.returncode == 0:
        st.success("✅ Data refreshed successfully!")
        df = pd.read_csv(f"data/{chain}_transfers.csv")
    else:
        st.error("❌ Failed to refresh data.")
        st.code(result.stderr)

# Load data
try:
    df = pd.read_csv(file_path)
    DECIMALS = 10 ** 6  # USDT uses 6 decimals
    df["value"] = df["value"] / DECIMALS
    if df.empty:
        st.warning(f"No data found for {chain.upper()}. Please run the fetch script.")
        st.stop()
except FileNotFoundError:
    st.error(f"File not found for {chain.upper()}. Please run the fetch script.")
    st.stop()

# Filter by wallet
if wallet_filter:
    df = df[df['from'].str.lower().str.contains(wallet_filter) | df['to'].str.lower().str.contains(wallet_filter)]

# Show raw data
st.subheader("📄 Transfer Data")
st.dataframe(df, use_container_width=True)

# Summary stats
st.subheader("📊 Summary")
col1, col2 = st.columns(2)
col1.metric("Total Transfers", len(df))
col2.metric("Total USDT Moved", round(df["value"].sum(), 2))

# Transfers by block chart
st.subheader("📈 Transfers by Block")
block_chart = df.groupby("block")["value"].sum().reset_index()
fig = px.line(block_chart, x="block", y="value", title="Total USDT per Block", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Anomaly detection
st.subheader("🚨 Anomaly Detection (Large Transfers)")
if len(df) > 10:
    iso = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = iso.fit_predict(df[['value']])
    anomalies = df[df['anomaly'] == -1]

    st.write(f"Detected {len(anomalies)} anomalous transfers (top 5 shown below):")
    st.dataframe(anomalies.head(), use_container_width=True)

    # Optional plot
    fig2 = px.scatter(anomalies, x="block", y="value", color="from", hover_data=["to"], title="Anomalous Transfers")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Not enough data for anomaly detection.")
