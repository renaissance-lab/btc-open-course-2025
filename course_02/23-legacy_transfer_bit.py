"""
使用 bit 库发送比特币 - 最简单版本
结合 mempool.space API 使用

优点：
- 代码简单，易于理解
- 自动处理 UTXO 和找零
- 自动处理签名

缺点：
- 依赖第三方 API
- 手续费计算可能不准确
- 网络拥堵时可能失败

"""

from bit import PrivateKeyTestnet
import time
import requests

def get_balance_from_mempool(address):
    """从 mempool.space 获取余额"""
    try:
        response = requests.get(f"https://mempool.space/testnet/api/address/{address}")
        if response.status_code == 200:
            data = response.json()
            chain_stats = data.get('chain_stats', {})
            balance = (chain_stats.get('funded_txo_sum', 0) - 
                      chain_stats.get('spent_txo_sum', 0))
            return balance
        return 0
    except Exception as e:
        print(f"获取余额失败: {e}")
        return 0

def send_bitcoin(from_wif, to_address, amount_satoshi):
    # 创建发送方密钥对象
    key = PrivateKeyTestnet(from_wif)
    
    # 打印发送方信息
    print(f"发送方地址: {key.address}")
    balance = get_balance_from_mempool(key.address)
    print(f"当前余额: {balance} satoshis")
    
    # 检查余额
    # if balance < amount_satoshi + 500:  # 加上预估手续费
    #     print(f"\n错误: 余额不足! 需要至少 {amount_satoshi + 500} satoshis")
    #     return
    
    # 创建交易输出
    outputs = [
        (to_address, amount_satoshi, 'satoshi')
    ]
    
    # 创建并广播交易
    try:
        # 先尝试创建交易
        tx_hex = key.create_transaction(outputs, fee=500)  # 手动设置手续费
        print("\n交易创建成功!")
        print(f"交易大小: {len(tx_hex)//2} bytes")
        
        # 询问是否广播
        confirm = input("\n是否广播交易？(y/n): ")
        if confirm.lower() == 'y':
            # 广播交易
            tx_id = key.send(outputs, fee=500)
            print("\n交易已广播!")
            print(f"交易ID: {tx_id}")
            print(f"在浏览器查看: https://mempool.space/testnet/tx/{tx_id}")
            
            # 等待几秒后检查余额变化
            time.sleep(3)
            new_balance = get_balance_from_mempool(key.address)
            print(f"\n当前余额: {new_balance} satoshis")
    
    except Exception as e:
        print(f"\n错误: {e}")

if __name__ == "__main__":
    # 测试网参数
    from_wif = "cPvd9PN8wykxyfec66x9fj48F3PTDBUUpC7zwkiq61zhU5sracJB"  # 发送方私钥
    to_address = "mkMgewbz1vEvuA5hFfNe6EsnPbvtnFj5LH"  # 接收地址
    amount = 1800  # 发送 1000 satoshis
    
    # 执行转账
    send_bitcoin(from_wif, to_address, amount) 