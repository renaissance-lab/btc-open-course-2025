r'''
比特币测试网地址查询工具 - 详细注释

本程序用于查询比特币测试网地址的信息，包括：
- 地址余额
- 交易历史
- UTXO信息
- 其他相关数据

本例只是链接了mempool.space的测试网API，如果当时网络堵塞，可以感受链接公众节点的不方便之处
参考Tools文件夹下的00--wallet_info.py，可以链接自己的节点，或者使用其他第三方节点
'''

from bit import PrivateKeyTestnet
from datetime import datetime
import requests

def format_btc(value):
    """将科学计数法转换为8位小数格式"""
    return f"{value:.8f}"

class BitcoinAddressInfo:
    def __init__(self):
        # 使用 mempool.space 的测试网 API
        self.base_url = "https://mempool.space/testnet/api"
    
    def get_address_info(self, address):
        """获取地址基本信息"""
        try:
            # 获取地址信息
            response = requests.get(f"{self.base_url}/address/{address}")
            if response.status_code == 200:
                data = response.json()
                
                # 获取 UTXO 信息
                utxos_response = requests.get(f"{self.base_url}/address/{address}/utxo")
                utxos = utxos_response.json() if utxos_response.status_code == 200 else []
                
                return {
                    'balance': sum(utxo.get('value', 0) for utxo in utxos) / 1e8,
                    'tx_count': data.get('chain_stats', {}).get('tx_count', 0),
                    'funded_txo_count': data.get('chain_stats', {}).get('funded_txo_count', 0),
                    'spent_txo_count': data.get('chain_stats', {}).get('spent_txo_count', 0),
                    'utxo_count': len(utxos)
                }
            return None
        except Exception as e:
            print(f"获取地址信息出错: {e}")
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
        """获取地址的交易历史"""
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
    # 测试网地址示例
    test_address = "msmkSKovoadUpdjbKMiancy6PnKowe4VP1"
    
    # 创建查询对象
    btc_info = BitcoinAddressInfo()
    
    print("===== 比特币测试网地址查询 =====")
    print(f"地址: {test_address}")
    
    # 获取基本信息
    info = btc_info.get_address_info(test_address)
    if info:
        print("\n=== 基本信息 ===")
        print(f"余额: {format_btc(info['balance'])} BTC")
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