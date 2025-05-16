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
    test_tx = "02000000000101e4a1ff79f47b4ce8f291676f98e013e3de6deefc6c63d7aedf4b2755af86d2690000000000ffffffff01c800000000000000225120060e50b842e9bf653206284c185dc209719f0d8437071cc1bf8ae4ee0f544d590140d503940bf4bbe8d722779a6d4d3f351b68e78908644f1f6016f4f469dc621ea623478b62667ddd677f12247ed9684329da4bf5995af2bf90114c88ef571e0a7900000000"
    
    result = broadcast_transaction(test_tx)
    print_broadcast_result(result)

