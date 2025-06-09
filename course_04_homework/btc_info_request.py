import requests
import json


MEMPOOL_BITCOIN_BASE_URL = "https://mempool.space/api"
MEMPOOL_TESTNET_BASE_URL = "https://mempool.space/testnet/api"
# MEMPOOL_TESTNET_BASE_URL = "https://mempool.space/signet/api"

def request_balance(addr):
    res = requests.get(f"https://api.blockchain.info/haskoin-store/btc/address/{addr}/balance", timeout=10).json()
    return res["confirmed"]

def get_mempool_base_url(chain_name="bitcoin"):
    if chain_name == "testnet":
        base_url = MEMPOOL_TESTNET_BASE_URL
    else:
        base_url = MEMPOOL_BITCOIN_BASE_URL
    return base_url

def request_fee_rate():
    res = requests.get(f"{MEMPOOL_BITCOIN_BASE_URL}/v1/fees/recommended", timeout=10).json()
    return res['fastestFee']

def request_utxo(addr,chain_name="bitcoin"):
    base_url = get_mempool_base_url(chain_name)
    url = f"{base_url}/address/{addr}/utxo"
    return requests.get(url, timeout=10).json()

def post_tx(raw_data,chain_name="bitcoin"):
    # base_url = get_mempool_base_url(chain_name)
    # url = f"{base_url}/tx"
    url = "https://blockstream.info/testnet/api/tx"
    print("url:",url)
    headers = {'Content-Type': 'text/plain'}
    return requests.post(url, data=raw_data, headers=headers, timeout=10).json()



   

