"""
比特币交易广播工具
"""

from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction
import requests
import json
import hashlib
import binascii

# 初始化比特币工具库
setup('testnet')

def extract_txid_from_hex(tx_hex):
    """
    从交易的十六进制字符串中提取TXID
    
    Args:
        tx_hex (str): 交易的十六进制字符串
        
    Returns:
        str: 交易ID (TXID)
    """
    try:
        # 将十六进制字符串转换为二进制数据
        tx_binary = binascii.unhexlify(tx_hex)
        
        # 对交易数据进行双重SHA256哈希
        hash1 = hashlib.sha256(tx_binary).digest()
        hash2 = hashlib.sha256(hash1).digest()
        
        # 反转字节顺序并转换为十六进制字符串
        txid = binascii.hexlify(hash2[::-1]).decode('ascii')
        
        return txid
    except Exception as e:
        print(f"提取TXID时出错: {e}")
        return None

def broadcast_transaction(tx_hex):
    """
    使用mempool.space API广播交易
    
    Args:
        tx_hex (str): 交易的十六进制字符串
        
    Returns:
        dict: 包含广播结果的字典
    """
    try:
        # 使用mempool.space API广播交易
        api_url = "https://mempool.space/testnet/api/tx"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(api_url, data=tx_hex, headers=headers)
        
        if response.status_code == 200:
            # 尝试从响应中提取txid，如果响应为空，则从交易数据中提取
            txid = response.text.strip('"') if response.text else extract_txid_from_hex(tx_hex)
            return {
                'success': True,
                'txid': txid,
                'error': None
            }
        else:
            return {
                'success': False,
                'txid': None,
                'error': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'txid': None,
            'error': str(e)
        }

def main():
    # 从命令行或用户输入获取交易十六进制字符串
    print("\n=== 比特币测试网交易广播工具 ===\n")
    tx_hex = input("请输入交易的十六进制字符串: ").strip()
    
    if not tx_hex:
        print("错误: 未提供交易数据")
        return
    
    print("\n正在广播交易...")
    result = broadcast_transaction(tx_hex)
    
    if result['success']:
        print("\n✅ 交易广播成功!")
        print(f"交易ID (TXID): {result['txid']}")
        print(f"查看交易: https://mempool.space/testnet/tx/{result['txid']}")
    else:
        print("\n❌ 交易广播失败!")
        print(f"错误信息: {result['error']}")
        
        # 检查是否是已经存在的交易
        if "Transaction already in block chain" in str(result['error']) or "already in the mempool" in str(result['error']) or "outputs already in utxo set" in str(result['error']):
            print("\n提示: 这个交易可能已经被广播过了。")
            
            # 尝试从交易十六进制中提取txid
            txid = extract_txid_from_hex(tx_hex)
            if txid:
                print(f"可能的交易ID: {txid}")
                print(f"查看交易: https://mempool.space/testnet/tx/{txid}")
            else:
                print("无法从交易数据中提取交易ID。请检查您最近的交易记录。")

if __name__ == "__main__":
    main()