import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

def connect_to_chain(chain: str) -> Web3:
    rpc_map = {
        "eth": os.getenv("INFURA_ETH"),
        "polygon": os.getenv("INFURA_POLYGON"),
        "bnb": os.getenv("INFURA_BNB")
    }
    
    if chain not in rpc_map:
        raise ValueError("Unsupported chain")

    rpc_url = rpc_map[chain]
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    if not web3.is_connected():
        raise ConnectionError(f"Failed to connect to {chain} at {rpc_url}")
    
    return web3
