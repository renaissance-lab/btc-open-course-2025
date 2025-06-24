#!/usr/bin/env python3
"""
BRC-20配置和常量
"""

# 私钥配置
PRIVATE_KEY_WIF = ""

# 网络配置
NETWORK = "testnet"

# 费用配置 (可调整)
FEE_CONFIG = {
    "commit_fee": 300,      # COMMIT交易费用
    "reveal_fee": 500,      # REVEAL交易费用
    "min_output": 546,      # 最小输出金额 (避免dust)
}

# BRC-20代币配置
TOKEN_CONFIG = {
    "deploy": {
        "p": "brc-20",
        "op": "deploy", 
        "tick": "PEPO",
        "max": "21000000",
        "lim": "1000"
    },
    "mint": {
        "p": "brc-20",
        "op": "mint",
        "tick": "DEMO", 
        "amt": "1000"
    }
}

# Inscription配置
INSCRIPTION_CONFIG = {
    "content_type": "text/plain;charset=utf-8",
    "content_type_hex": "746578742f706c61696e3b636861727365743d7574662d38",
    "ord_marker": "6f7264"  # "ord"
}

def get_brc20_json(op_type="deploy"):
    """获取BRC-20 JSON字符串"""
    if op_type not in TOKEN_CONFIG:
        raise ValueError(f"不支持的操作类型: {op_type}")
    
    import json
    return json.dumps(TOKEN_CONFIG[op_type], separators=(',', ':'))

def get_brc20_hex(op_type="deploy"):
    """获取BRC-20 JSON的hex编码"""
    json_str = get_brc20_json(op_type)
    return json_str.encode('utf-8').hex()

def calculate_inscription_amount():
    """计算需要发送到临时地址的金额"""
    return FEE_CONFIG["min_output"] + FEE_CONFIG["reveal_fee"]

if __name__ == "__main__":
    print("=== BRC-20配置信息 ===")
    print(f"网络: {NETWORK}")
    print(f"代币信息: {get_brc20_json('deploy')}")
    print(f"Mint信息: {get_brc20_json('mint')}")
    print(f"inscription金额: {calculate_inscription_amount()} sats")
    print(f"费用配置: {FEE_CONFIG}")