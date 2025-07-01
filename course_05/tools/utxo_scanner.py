import requests
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_utxos(address: str, min_value: int = 600) -> List[Dict]:
    """
    获取地址的UTXO列表
    
    Args:
        address: 比特币地址
        min_value: 最小UTXO值（聪）
        
    Returns:
        List[Dict]: UTXO列表
    """
    url = f"https://mempool.space/testnet/api/address/{address}/utxo"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        utxos = response.json()
        
        # 过滤出大于最小值的UTXO
        filtered_utxos = [
            utxo for utxo in utxos
            if utxo.get('value', 0) >= min_value
        ]
        
        if not filtered_utxos:
            raise Exception(f"No UTXOs found with value >= {min_value} satoshis")
            
        # 打印UTXO信息
        print("\nUTXO 信息:")
        print("=" * 50)
        for i, utxo in enumerate(filtered_utxos, 1):
            print(f"UTXO #{i}:")
            print(f"  交易ID: {utxo.get('txid')}")
            print(f"  输出索引: {utxo.get('vout')}")
            print(f"  金额: {utxo.get('value')} 聪 ({utxo.get('value')/100000000:.8f} BTC)")
            print()
            
        return filtered_utxos
        
    except Exception as e:
        logger.error(f"Error fetching UTXOs: {e}")
        raise 