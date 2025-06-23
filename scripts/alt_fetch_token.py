import os
import json
import requests
import pandas as pd

RPCS = {
    "eth": "https://mainnet.infura.io/v3/48217549432b45008a27d82627742b5b",
    "polygon": "https://polygon-bor.publicnode.com",
    "bnb": "https://bsc.publicnode.com"
}

TOKENS = {
    "eth": "0xdAC17F958D2ee523a2206206994597C13D831ec7",      # USDT
    "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDT
    "bnb": "0x55d398326f99059fF775485246999027B3197955"       # USDT
}

def to_hex(n):
    return hex(n)

def fetch_logs(chain):
    print(f"\nFetching logs for {chain.upper()}")

    rpc = RPCS[chain]
    token = TOKENS[chain]
    headers = {"Content-Type": "application/json"}

    try:
        # Get latest block
        resp = requests.post(rpc, json={
            "jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1
        }, headers=headers)
        latest_block = int(resp.json()["result"], 16)
        from_block = to_hex(latest_block - (1000 if chain == "polygon" else 100))
        to_block = to_hex(latest_block)

        topic0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"  # Transfer()

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [{
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": token,
                "topics": [topic0]
            }],
            "id": 42
        }

        response = requests.post(rpc, json=payload, headers=headers).json()

        if "error" in response:
            print(f" Error fetching {chain}: {response['error']}")
            return

        logs = response["result"]
        rows = []
        for log in logs:
            tx = log["transactionHash"]
            blk = int(log["blockNumber"], 16)
            from_addr = "0x" + log["topics"][1][-40:]
            to_addr = "0x" + log["topics"][2][-40:]
            value = int(log["data"], 16) / 1e6  # USDT

            rows.append({
                "tx_hash": tx,
                "block": blk,
                "from": from_addr,
                "to": to_addr,
                "value": value
            })

        if rows:
            df = pd.DataFrame(rows)
            os.makedirs("data", exist_ok=True)
            df.to_csv(f"data/{chain}_transfers.csv", index=False)
            print(f" Saved {len(df)} logs to data/{chain}_transfers.csv")
        else:
            print(" No logs found.")

    except Exception as e:
        print(f" Exception on {chain}: {e}")

if __name__ == "__main__":
    for chain in ["eth", "polygon", "bnb"]:
        fetch_logs(chain)
