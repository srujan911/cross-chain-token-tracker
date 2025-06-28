import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.alt_fetch_token import fetch_logs

# ------------------- Page Config -------------------
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

# ------------------- Chain Selection -------------------
chain = st.sidebar.selectbox("Choose a chain", ["eth", "polygon", "bnb"])
wallet_filter = st.sidebar.text_input("Filter by wallet address (optional)").lower()

file_path = f"data/{chain}_transfers.csv"

# Manual Fetch Button
if st.button("🔁 Refresh Data Now"):
    with st.spinner("Fetching new data..."):
        import subprocess
        result = subprocess.run(["python", "scripts/alt_fetch_token.py"], capture_output=True, text=True)
    if result.returncode == 0:
        st.success("✅ Data refreshed successfully!")
    else:
        st.error("❌ Failed to refresh data.")
        st.code(result.stderr)

# Load CSV
try:
    df = pd.read_csv(file_path)
    DECIMALS = 10**6  # USDT uses 6 decimals
    df["value"] = df["value"] / DECIMALS
    if df.empty:
        st.warning(f"No data found for {chain.upper()}. Please run the fetch script.")
        st.stop()
except FileNotFoundError:
    st.error(f"File not found for {chain.upper()}. Please run the fetch script.")
    st.stop()

# Filter by wallet
if wallet_filter:
    df = df[df["from"].str.lower().str.contains(wallet_filter) | df["to"].str.lower().str.contains(wallet_filter)]

# ------------------- Anomaly Detection (Run Once) -------------------
if len(df) > 10:
    iso = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = iso.fit_predict(df[['value']])
else:
    df['anomaly'] = 1  # mark all normal if insufficient data



# ------------------- Tabs -------------------
tab1, tab2 = st.tabs(["📄 Transfer Summary", "📊 Analytics"])

# ------------------- Tab 1: Summary -------------------
with tab1:
    st.subheader("📄 Transfer Data")
    st.dataframe(df, use_container_width=True)

    st.subheader("📊 Summary")
    col1, col2 = st.columns(2)
    col1.metric("Total Transfers", len(df))
    col2.metric("Total USDT Moved", round(df["value"].sum(), 2))

    st.subheader("📈 Transfers by Block")
    block_chart = df.groupby("block")["value"].sum().reset_index()
    fig = px.line(block_chart, x="block", y="value", title="Total USDT per Block", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚨 Anomaly Detection")
    anomalies = df[df['anomaly'] == -1]
    if not anomalies.empty:
        st.write(f"Detected {len(anomalies)} anomalous transfers (top 5 shown below):")
        st.dataframe(anomalies.head(), use_container_width=True)

        fig2 = px.scatter(anomalies, x="block", y="value", color="from", hover_data=["to"], title="Anomalous Transfers")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No anomalies detected.")
        # ------------------- Auto Refresh -------------------
@st.cache_data(ttl=120)
def auto_refresh_data(chain):
    fetch_logs(chain)
    return pd.read_csv(f"data/{chain}_transfers.csv")

if st.button("🔄 Auto-Refresh Data Now"):
    try:
        df = auto_refresh_data(chain)
        st.success("Data refreshed successfully!")
    except Exception as e:
        st.error(f"Refresh failed: {e}")

# ------------------- Tab 2: Analytics -------------------
with tab2:
    st.subheader("🧠 Transaction Classification")

    def classify_transaction(value):
        if value > 10000:
            return "🐳 Whale"
        elif value < 0.001:
            return "🐜 Spam"
        else:
            return "⚖️ Normal"

    df["category"] = df["value"].apply(classify_transaction)
    st.dataframe(df[["tx_hash", "from", "to", "value", "category"]], use_container_width=True)

    category_counts = df["category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]
    fig = px.pie(category_counts, names="Category", values="Count", title="Transaction Categories")
    st.plotly_chart(fig, use_container_width=True)

    # Anomaly Classification
    st.subheader("📊 Anomaly Type Classification")
    df_anomaly = df[df["anomaly"] == -1].copy()

    def classify_anomaly(row):
        if row["value"] > 100000:
            return "Whale"
        elif row["value"] < 0.001:
            return "Spam"
        else:
            return "Other"

    if not df_anomaly.empty:
        df_anomaly["type"] = df_anomaly.apply(classify_anomaly, axis=1)
        fig = px.pie(df_anomaly, names="type", title="Anomaly Categories", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_anomaly[["tx_hash", "from", "to", "value", "type"]])
    else:
        st.info("No anomalies to classify.")
