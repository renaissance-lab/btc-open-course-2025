r'''
比特币测试网地址查询工具 - 连接本地节点

从这里又可以看出全节点的不完美，没有成熟的做得好的节点的API功能完善
特别是要遍历UTXO等操作
'''

from bitcoin import SelectParams
from bitcoin.rpc import Proxy
from datetime import datetime

def format_btc(value):
    """将科学计数法转换为8位小数格式"""
    return f"{value:.8f}"

class BitcoinAddressInfo:
    def __init__(self):
        # 设置测试网
        SelectParams('testnet')
        
        print("正在连接到本地测试网节点...")
        self.proxy = Proxy(
            service_url="http://username:password@127.0.0.1:18332",
            timeout=30
        )
        
        # 测试连接并显示区块高度
        info = self.proxy._call('getblockchaininfo')
        print(f"节点连接成功，当前区块高度: {info['blocks']}")
        
        # 加载钱包
        try:
            loaded_wallets = self.proxy._call('listwallets')
            if 'testwallet' not in loaded_wallets:
                self.proxy._call('loadwallet', 'testwallet')
            print("钱包加载成功")
        except Exception as e:
            print(f"加载钱包失败: {e}")
    
    def get_address_info(self, address):
        """获取地址基本信息"""
        try:
            # 使用 scantxoutset 获取地址UTXO
            result = self.proxy._call('scantxoutset', 'start', [f"addr({address})"])
            if result:
                return {
                    'balance': result['total_amount'],
                    'utxo_count': len(result['unspent']),
                    'success': result['success']
                }
            return None
        except Exception as e:
            print(f"获取地址信息出错: {e}")
            return None

    def get_address_utxos(self, address):
        """获取地址的UTXO信息"""
        try:
            result = self.proxy._call('scantxoutset', 'start', [f"addr({address})"])
            utxos = []
            for utxo in result.get('unspent', []):
                tx_info = self.proxy._call('gettransaction', utxo['txid'])
                utxos.append({
                    'txid': utxo['txid'],
                    'vout': utxo['vout'],
                    'value': utxo['amount'],
                    'confirmations': tx_info['confirmations'],
                    'blockhash': tx_info.get('blockhash', 'pending')
                })
            return utxos
        except Exception as e:
            print(f"获取UTXO信息出错: {e}")
            return None

    def get_transaction_history(self, address, limit=10):
        """获取地址的交易历史"""
        try:
            # 先获取地址的UTXO
            utxos = self.get_address_utxos(address)
            txids = set()
            
            # 收集所有交易ID
            for utxo in utxos:
                txids.add(utxo['txid'])
            
            # 获取每个交易的详细信息
            txs = []
            for txid in list(txids)[:limit]:
                tx_info = self.proxy._call('gettransaction', txid)
                txs.append({
                    'txid': txid,
                    'confirmations': tx_info['confirmations'],
                    'time': tx_info['time'],
                    'amount': tx_info['amount'],
                    'fee': tx_info.get('fee', 0),
                    'blockhash': tx_info.get('blockhash', 'pending')
                })
            return txs
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
        print(f"UTXO数量: {info['utxo_count']}")
        print(f"扫描成功: {'是' if info['success'] else '否'}")
    
    # 获取UTXO信息
    utxos = btc_info.get_address_utxos(test_address)
    if utxos:
        print("\n=== UTXO信息 ===")
        for utxo in utxos:
            print(f"交易ID: {utxo['txid']}")
            print(f"输出索引: {utxo['vout']}")
            print(f"金额: {format_btc(utxo['value'])} BTC")
            print(f"确认数: {utxo['confirmations']}")
            print("---")
    
    # 获取交易历史
    txs = btc_info.get_transaction_history(test_address)
    if txs:
        print("\n=== 最近交易历史 ===")
        for tx in txs:
            print(f"交易ID: {tx['txid']}")
            print(f"确认数: {tx['confirmations']}")
            print(f"金额: {format_btc(tx['amount'])} BTC")
            print(f"时间: {datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d %H:%M:%S')}")
            print("---")


if __name__ == "__main__":
    main()