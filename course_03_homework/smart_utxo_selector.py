"""
智能UTXO选择器

该脚本用于从一个地址的多个UTXO中智能选择合适的组合来满足指定的交易金额。
支持多种UTXO选择策略：
1. 贪心算法：优先选择最大的UTXO
2. 最小变化算法：尽量选择接近目标金额的UTXO组合，减少找零
3. 合并小额UTXO：优先选择小额UTXO，帮助清理钱包

使用方法:
python smart_utxo_selector.py <地址> <目标金额> [--strategy <选择策略>] [--network <网络>]
"""

import requests
import json
import sys
import argparse
from decimal import Decimal
from typing import List, Dict, Any, Tuple

# 配置
BASE_URL = "https://mempool.space"
NETWORK = "testnet"  # 默认使用testnet网络
SATOSHI_PER_BTC = 100000000

class SmartUTXOSelector:
    def __init__(self, network=NETWORK):
        """初始化UTXO选择器"""
        self.network = network
        self.base_url = f"{BASE_URL}/{network}"
    
    def get_utxos(self, address: str) -> List[Dict[str, Any]]:
        """获取地址的所有UTXO"""
        url = f"{self.base_url}/api/address/{address}/utxo"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"获取UTXO失败: {response.status_code} {response.text}")
        
        utxos = response.json()
        print(f"地址 {address} 的UTXO列表:")
        for i, utxo in enumerate(utxos):
            print(f"  UTXO #{i+1}: {utxo['txid']}:{utxo['vout']} - {utxo['value']} satoshis")
        
        return utxos
    
    def select_utxos_greedy(self, utxos: List[Dict[str, Any]], target_amount: int) -> Tuple[List[Dict[str, Any]], int]:
        """贪心算法：优先选择最大的UTXO"""
        # 按金额降序排序
        sorted_utxos = sorted(utxos, key=lambda x: x['value'], reverse=True)
        selected_utxos = []
        total_selected = 0
        
        for utxo in sorted_utxos:
            if total_selected >= target_amount:
                break
            selected_utxos.append(utxo)
            total_selected += utxo['value']
        
        if total_selected < target_amount:
            raise Exception(f"UTXO总额不足，需要{target_amount}，仅有{total_selected}")
            
        return selected_utxos, total_selected
    
    def select_utxos_min_change(self, utxos: List[Dict[str, Any]], target_amount: int) -> Tuple[List[Dict[str, Any]], int]:
        """最小找零算法：尝试找到最接近目标金额的UTXO组合"""
        # 首先检查是否有单个UTXO接近目标值
        for utxo in utxos:
            if utxo['value'] >= target_amount:
                return [utxo], utxo['value']
        
        # 否则尝试组合多个UTXO，使找零最小
        n = len(utxos)
        # 动态规划数组，dp[i]表示金额i需要的最小UTXO数量
        dp = [float('inf')] * (target_amount + 1)
        dp[0] = 0
        
        # 记录每个金额对应的UTXO组合
        utxo_combinations = [[] for _ in range(target_amount + 1)]
        utxo_combinations[0] = []
        
        # 填充动态规划表
        for i in range(n):
            utxo_value = utxos[i]['value']
            for j in range(target_amount, utxo_value - 1, -1):
                if dp[j - utxo_value] + 1 < dp[j]:
                    dp[j] = dp[j - utxo_value] + 1
                    utxo_combinations[j] = utxo_combinations[j - utxo_value] + [i]
        
        # 寻找满足条件的最小组合
        for j in range(target_amount, len(dp) - 1):
            if dp[j] != float('inf'):
                selected_indices = utxo_combinations[j]
                selected_utxos = [utxos[i] for i in selected_indices]
                total_value = sum(utxo['value'] for utxo in selected_utxos)
                return selected_utxos, total_value
        
        # 如果没有找到精确匹配，就使用贪心算法
        return self.select_utxos_greedy(utxos, target_amount)
    
    def select_utxos_consolidate(self, utxos: List[Dict[str, Any]], target_amount: int) -> Tuple[List[Dict[str, Any]], int]:
        """合并小额UTXO算法：优先选择小额UTXO，帮助清理钱包"""
        # 按金额升序排序
        sorted_utxos = sorted(utxos, key=lambda x: x['value'])
        selected_utxos = []
        total_selected = 0
        
        for utxo in sorted_utxos:
            selected_utxos.append(utxo)
            total_selected += utxo['value']
            if total_selected >= target_amount:
                break
        
        if total_selected < target_amount:
            raise Exception(f"UTXO总额不足，需要{target_amount}，仅有{total_selected}")
            
        return selected_utxos, total_selected
    
    def select_utxos(self, address: str, target_amount: int, strategy="greedy") -> Tuple[List[Dict[str, Any]], int]:
        """根据策略选择UTXO"""
        utxos = self.get_utxos(address)
        
        if not utxos:
            raise Exception(f"地址 {address} 没有可用的UTXO")
        
        strategies = {
            "greedy": self.select_utxos_greedy,
            "min_change": self.select_utxos_min_change,
            "consolidate": self.select_utxos_consolidate
        }
        
        if strategy not in strategies:
            raise ValueError(f"不支持的策略: {strategy}. 可用策略: {', '.join(strategies.keys())}")
        
        print(f"使用 {strategy} 策略选择UTXO")
        return strategies[strategy](utxos, target_amount)
    
    def create_transaction_input_template(self, selected_utxos: List[Dict[str, Any]]) -> str:
        """创建交易输入模板"""
        tx_template = "{\n"
        tx_template += '  "inputs": [\n'
        
        for i, utxo in enumerate(selected_utxos):
            tx_template += f'    {{\n'
            tx_template += f'      "txid": "{utxo["txid"]}",\n'
            tx_template += f'      "vout": {utxo["vout"]},\n'
            tx_template += f'      "value": {utxo["value"]}\n'
            tx_template += f'    }}{"," if i < len(selected_utxos) - 1 else ""}\n'
        
        tx_template += '  ],\n'
        tx_template += '  "outputs": [\n    // 请在这里添加您的输出\n  ]\n}'
        
        return tx_template
    
    def get_fee_estimate(self) -> Dict[str, int]:
        """获取费率估计"""
        url = f"{self.base_url}/api/v1/fees/recommended"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"获取费率失败: {response.status_code} {response.text}")
        
        return response.json()
    
    def estimate_tx_size(self, input_count: int, output_count: int = 2) -> int:
        """估计交易大小（字节）"""
        # 这是一个简化的估计，实际大小取决于脚本类型和见证数据
        # 假设P2WPKH输入和P2WPKH输出
        base_size = 10  # 版本 + 锁定时间
        input_weight = 41 * 4  # P2WPKH输入的权重单位
        output_weight = 31 * 4  # P2WPKH输出的权重单位
        
        total_weight = base_size * 4 + input_count * input_weight + output_count * output_weight
        virtual_size = (total_weight + 3) // 4  # 向上取整到最接近的整数
        
        return virtual_size
    
    def estimate_fee(self, input_count: int, output_count: int = 2, fee_rate: int = None) -> int:
        """估计交易费用（satoshis）"""
        if fee_rate is None:
            fee_estimates = self.get_fee_estimate()
            fee_rate = fee_estimates.get('hourFee', 10)  # 默认使用hourFee，如果没有则使用10 sat/vB
        
        tx_size = self.estimate_tx_size(input_count, output_count)
        fee = tx_size * fee_rate
        
        return fee

def btc_to_satoshi(btc_amount: float) -> int:
    """将BTC转换为satoshi"""
    return int(Decimal(str(btc_amount)) * SATOSHI_PER_BTC)

def satoshi_to_btc(satoshi_amount: int) -> float:
    """将satoshi转换为BTC"""
    return float(Decimal(satoshi_amount) / SATOSHI_PER_BTC)

def main():
    parser = argparse.ArgumentParser(description='智能UTXO选择器')
    parser.add_argument('address', help='比特币地址')
    parser.add_argument('amount', type=float, help='目标金额（BTC）')
    parser.add_argument('--strategy', default='greedy', choices=['greedy', 'min_change', 'consolidate'],
                        help='UTXO选择策略: greedy(默认)、min_change或consolidate')
    parser.add_argument('--network', default=NETWORK, help=f'比特币网络 (默认: {NETWORK})')
    
    args = parser.parse_args()
    
    # 将BTC转换为satoshi
    target_satoshis = btc_to_satoshi(args.amount)
    
    try:
        selector = SmartUTXOSelector(network=args.network)
        
        # 获取费率估计
        fee_estimates = selector.get_fee_estimate()
        print(f"当前费率估计: {json.dumps(fee_estimates, indent=2)}")
        
        # 选择UTXO
        selected_utxos, total_value = selector.select_utxos(args.address, target_satoshis, args.strategy)
        
        # 估计费用
        estimated_fee = selector.estimate_fee(len(selected_utxos))
        
        # 计算找零
        change = total_value - target_satoshis - estimated_fee
        
        print("\n=== 选择结果 ===")
        print(f"目标金额: {args.amount} BTC ({target_satoshis} satoshis)")
        print(f"选择的UTXO数量: {len(selected_utxos)}")
        print(f"选择的UTXO总价值: {satoshi_to_btc(total_value):.8f} BTC ({total_value} satoshis)")
        print(f"估计费用: {satoshi_to_btc(estimated_fee):.8f} BTC ({estimated_fee} satoshis)")
        print(f"找零金额: {satoshi_to_btc(change):.8f} BTC ({change} satoshis)")
        
        print("\n=== 选择的UTXO详情 ===")
        for i, utxo in enumerate(selected_utxos):
            print(f"UTXO #{i+1}: {utxo['txid']}:{utxo['vout']} - {satoshi_to_btc(utxo['value']):.8f} BTC ({utxo['value']} satoshis)")
        
        print("\n=== 交易输入模板 ===")
        print(selector.create_transaction_input_template(selected_utxos))
        
        print("\n您可以使用此模板作为构建交易的基础。请添加您的输出并进行签名。")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
