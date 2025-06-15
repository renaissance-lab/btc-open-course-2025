from datetime import datetime
import requests

def format_btc(value):
    return "{:0.8f}".format(value)

class BitcoinAddressInfo:
    def __init__(self):
        self.base_url = "https://mempool.space/testnet/api"
    
    def get_address_info(self, address):
        try:
            response = requests.get(f"{self.base_url}/address/{address}")
            if response.status_code == 200:
                data = response.json()
                
                utxos_response = requests.get(f"{self.base_url}/address/{address}/utxo")
                utxos = utxos_response.json() if utxos_response.status_code == 200 else []
                
                return {
                    'balance': format_btc(sum(utxo.get('value', 0) for utxo in utxos) / 1e8),
                    'tx_count': data.get('chain_stats', {}).get('tx_count', 0),
                    'funded_txo_count': data.get('chain_stats', {}).get('funded_txo_count', 0),
                    'spent_txo_count': data.get('chain_stats', {}).get('spent_txo_count', 0),
                    'utxo_count': len(utxos)
                }
            return None
        except Exception as e:
            print(f"Error fetching address info: {e}")
            return None
    
    def get_address_utxos(self, address):
        """获取地址的UTXO信息"""
        try:
            response = requests.get(f"{self.base_url}/address/{address}/utxo")
            if response.status_code == 200:
                utxos = []
                for utxo in response.json():
                    utxos.append({
                        'txid': utxo.get('txid'),
                        'vout': utxo.get('vout'),
                        'value': utxo.get('value', 0) / 1e8,
                        'status': utxo.get('status', {}).get('confirmed', False)
                    })
                return utxos
            return None
        except Exception as e:
            print(f"获取UTXO信息出错: {e}")
            return None

    def get_transaction_history(self, address, limit=10):
        try:
            response = requests.get(f"{self.base_url}/address/{address}/txs")
            if response.status_code == 200:
                txs = []
                for tx in response.json()[:limit]:
                    tx_info = {
                        'txid': tx.get('txid'),
                        'block_height': tx.get('status', {}).get('block_height', 'unconfirmed'),
                        'confirmed': tx.get('status', {}).get('confirmed', False),
                        'fee': tx.get('fee', 0) / 1e8,
                        'size': tx.get('size', 0),
                        'time': tx.get('status', {}).get('block_time')
                    }
                    txs.append(tx_info)
                return txs
            return None
        except Exception as e:
            print(f"获取交易历史出错: {e}")
            return None



def main():
    btc_info = BitcoinAddressInfo()
    test_address = "cQypWJeasiAFVubwDVqW9KmPJ2mMPKVmtjrrqb4t39Zgt5qF3Eos"

    # 获取基本信息
    info = btc_info.get_address_info(test_address)
    if info:
        print("=== 基本信息 ===")
        print(f"余额: {info['balance']} BTC")
        print(f"交易数量: {info['tx_count']}")
        print(f"已收到: {info['funded_txo_count']}")
        print(f"已发送: {info['spent_txo_count']}")
        print(f"UTXO数量: {info['utxo_count']}")

    # 获取UTXO信息
    utxos = btc_info.get_address_utxos(test_address)
    if utxos:
        print("\n=== UTXO信息 ===")
        for utxo in utxos:
            print(f"交易ID: {utxo['txid']}")
            print(f"输出索引: {utxo['vout']}")
            print(f"金额: {format_btc(utxo['value'])} BTC")
            print(f"状态: {'已确认' if utxo['status'] else '未确认'}")
            print("---")

    # 获取交易历史
    txs = btc_info.get_transaction_history(test_address)
    if txs:
        print("\n=== 最近交易历史 ===")
        for tx in txs:
            print(f"交易ID: {tx['txid']}")
            print(f"区块高度: {tx['block_height']}")
            print(f"确认状态: {'已确认' if tx['confirmed'] else '未确认'}")
            print(f"手续费: {format_btc(tx['fee'])} BTC")
            print(f"大小: {tx['size']} bytes")
            print(f"时间: {datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d %H:%M:%S')}")
            print("---")



if __name__ == "__main__":
    main()