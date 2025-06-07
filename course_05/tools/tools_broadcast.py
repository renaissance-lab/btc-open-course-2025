"""
比特币交易广播工具

用途：
- 将签名后的交易广播到比特币网络
- 支持测试网和主网
- 使用 mempool.space API

使用示例：
from tools.tools_broadcast import broadcast_transaction

tx_hex = "020000000153b775..."
result = broadcast_transaction(tx_hex, network="testnet")
"""

import requests

def broadcast_transaction(signed_tx_hex: str, network: str = "testnet") -> dict:
    """
    广播已签名的比特币交易
    
    参数:
        signed_tx_hex: 已签名的交易的十六进制字符串
        network: 'testnet' 或 'mainnet'
        
    返回:
        dict: {
            'success': bool,
            'txid': str,
            'error': str,
            'url': str
        }
    """
    
    # 根据网络选择 API
    base_url = "https://mempool.space"
    if network == "testnet":
        base_url += "/testnet"
    
    api_url = f"{base_url}/api/tx"
    explorer_url = f"{base_url}/tx"
    
    try:
        # 广播交易
        response = requests.post(api_url, data=signed_tx_hex)
        
        if response.status_code == 200:
            txid = response.text
            return {
                'success': True,
                'txid': txid,
                'error': None,
                'url': f"{explorer_url}/{txid}"
            }
        else:
            return {
                'success': False,
                'txid': None,
                'error': response.text,
                'url': None
            }
            
    except Exception as e:
        return {
            'success': False,
            'txid': None,
            'error': str(e),
            'url': None
        }

def print_broadcast_result(result: dict):
    """打印广播结果"""
    if result['success']:
        print("\n=== 交易广播成功 ===")
        print(f"交易ID: {result['txid']}")
        print(f"浏览器查看: {result['url']}")
    else:
        print("\n=== 交易广播失败 ===")
        print(f"错误信息: {result['error']}")

# 使用示例
if __name__ == "__main__":
    # 测试交易
    test_tx = "020000000001019e9fb14b964c47b3d38e29116baf7fbb71b2a8818fbf90ec342a7aa823645f110100000000ffffffff01400600000000000022512085c58676d98f62df6a5be6632156e4bc684659e894bd4505b48920559894c47b03406bc38ac6c4d6d9e449e1a62f8158e2bd107e060babb7d1ab71d3a70a288ba7a156538aa255e99860b61a809cb7e4d7e993f543f13fa27aecd3871c8ed055aa5c222084b5951609b76619a1ce7f48977b4312ebe226987166ef044bfb374ceef63af5ac61c050be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d3fe78d8523ce9603014b28739a51ef826f791aa17511e617af6dc96a8f10f659e12273573f45d51a1c48a75e76fe1d955f9f00acb1fe288510ab242f0851a7bf500000000"
    
    result = broadcast_transaction(test_tx)
    print_broadcast_result(result)

