# 🔗 Cross-Chain Token Tracker

A real-time dashboard to visualize **USDT token transfers** across **Ethereum**, **BNB**, and **Polygon** blockchains.

---

## 🚀 Features

- View token transfers on Ethereum, BNB, and Polygon
- Filter by wallet address (`from` / `to`)
- Calculate total USDT moved, total transactions
- Plot transaction volume per block
- Detect abnormal transfers using AI (Isolation Forest)
- 🔁 Manual or auto-refresh using a Streamlit button

---

## 📸 Preview

![Dashboard Screenshot](link-to-screenshot-if-you-upload-it)

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – for dashboard
- **Pandas** – for data processing
- **Web3.py** – for blockchain RPC access
- **Plotly Express** – for plotting
- **Scikit-Learn** – anomaly detection (Isolation Forest)

---

## 📂 Project Structure

cross-chain-token-tracker/

├── dashboard/ # Streamlit dashboard

├── scripts/ # Data fetching scripts (RPC logs)

├── data/ # Output CSV logs (ETH, BNB, Polygon)

├── utils/ # Helper modules

├── .env # Environment config (RPC URLs)

├── requirements.txt # Dependencies

└── README.md

## ⚙️ Getting Started

1. **Clone the repository**
   
   git clone https://github.com/srujan911/cross-chain-token-tracker.git
   cd cross-chain-token-tracker

2. **Create and activate a virtual environment**

    
    python -m venv .venv
    .venv\Scripts\activate  # on Windows

3.**Install dependencies**

    pip install -r requirements.txt

4.**Set up .env**

    ETH_RPC_URL=https://your-eth-node
    BNB_RPC_URL=https://your-bnb-node
    POLYGON_RPC_URL=https://your-polygon-node

5.**Run the app**
    streamlit run dashboard/app.py
