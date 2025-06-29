#!/usr/bin/env python3
"""
UTXO扫描和选择工具
"""

import requests

def get_available_utxos(addr):
    """
    实时获取当前可用的UTXO列表（从Blockstream API）
    """
    url = "https://blockstream.info/testnet/api/address/" + addr + "/utxo"
    print(url)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        utxo_list = resp.json()
        utxos = []
        for u in utxo_list:
            utxos.append({
                "txid": u["txid"],
                "vout": u["vout"],
                "amount": u["value"],
                "note": "API获取"
            })
        return utxos
    except Exception as e:
        print(f"[错误] 获取UTXO失败: {e}")
        return []

def select_best_utxo(addr, min_amount=1500):
    """
    选择最适合的UTXO
    
    Args:
        min_amount: 最小金额要求
    
    Returns:
        dict: 选中的UTXO，如果没有合适的返回None
    """
    utxos = get_available_utxos(addr)
    
    print("=== 扫描可用UTXO ===")
    for i, utxo in enumerate(utxos):
        status = "✅" if utxo["amount"] >= min_amount else "❌"
        print(f"  {i+1}. {utxo['txid'][:16]}...:{utxo['vout']} = {utxo['amount']} sats - {utxo['note']} {status}")
    
    # 选择金额最大且满足要求的UTXO
    suitable_utxos = [u for u in utxos if u["amount"] >= min_amount]
    
    if not suitable_utxos:
        print(f"❌ 没有找到满足最小金额 {min_amount} sats 的UTXO")
        return None
    
    # 返回金额最大的
    selected = max(suitable_utxos, key=lambda x: x["amount"])
    print(f"\n✅ 选择UTXO: {selected['txid'][:16]}...:{selected['vout']} ({selected['amount']} sats)")
    print(f"选择原因: {selected['note']}")
    
    return selected

def show_utxo_list(addr):
    """显示所有UTXO列表"""
    utxos = get_available_utxos(addr)
    print("=== 所有可用UTXO ===")
    for i, utxo in enumerate(utxos):
        print(f"  {i+1}. TxID: {utxo['txid']}")
        print(f"      Vout: {utxo['vout']}")
        print(f"      金额: {utxo['amount']} sats")
        print(f"      备注: {utxo['note']}")
        print()

if __name__ == "__main__":
    show_utxo_list("tb1pa3gu4mqkgxcv8yjhh8mfcp93jha3exxck8her2u6j5dgn6gmmuwsd7gg9s")
    print()
    selected = select_best_utxo("tb1pa3gu4mqkgxcv8yjhh8mfcp93jha3exxck8her2u6j5dgn6gmmuwsd7gg9s", 1500)
    if selected:
        print(f"\n推荐使用: {selected['txid']}:{selected['vout']}")