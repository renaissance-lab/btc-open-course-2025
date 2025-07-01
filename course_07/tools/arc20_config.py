#!/usr/bin/env python3
"""
ARC-20/Atomicals配置和常量
"""

# 私钥配置 (复用BRC-20的私钥)
PRIVATE_KEY_WIF = ""

# 网络配置
NETWORK = "testnet"

# 费用配置 (可调整)
FEE_CONFIG = {
    "commit_fee": 300,      # COMMIT交易费用
    "reveal_fee": 500,      # REVEAL交易费用
    "min_output": 546,      # 最小输出金额 (避免dust)
}

# ARC-20/Atomicals协议配置
PROTOCOL_CONFIG = {
    "protocol": "atom",     # 协议标识
    "op_type": "dmt",       # 操作类型: dmt, deploy, mint
    "bitworkc": "000000",   # commit挖矿难度前缀
    "bitworkr": "6238",     # reveal挖矿难度前缀
    "mint_ticker": "sophon" # 代币符号
}

# Atomicals Payload配置
PAYLOAD_CONFIG = {
    "deploy": {
        "args": {
            "bitworkc": "000000",
            "bitworkr": "6238",
            "mint_ticker": "DEMO",
            "max": "21000000",
            "lim": "1000"
        }
    },
    "mint": {
        "args": {
            "bitworkc": "000000",
            "bitworkr": "6238", 
            "mint_ticker": "sophon"
        }
    }
}

# Inscription配置
INSCRIPTION_CONFIG = {
    "protocol_hex": "61746f6d",  # "atom"
    "op_type_hex": "646d74"      # "dmt"
}

def get_atomicals_payload(op_type="mint", time_val=None, nonce=0):
    """获取Atomicals Payload (CBOR编码)"""
    if op_type not in PAYLOAD_CONFIG:
        raise ValueError(f"不支持的操作类型: {op_type}")
    
    import time
    import cbor2
    
    # 复制基础配置
    payload = PAYLOAD_CONFIG[op_type].copy()
    
    # 添加动态参数 - 确保time和nonce在最前面
    if time_val is None:
        time_val = int(time.time())
    
    # 重新构建args字典，确保字段顺序一致
    args = {
        "time": time_val,
        "nonce": nonce
    }
    
    # 添加其他字段
    for key, value in payload["args"].items():
        if key not in ["time", "nonce"]:  # 跳过已添加的字段
            args[key] = value
    
    payload["args"] = args
    
    return cbor2.dumps(payload)

def get_atomicals_payload_hex(op_type="mint", time_val=None, nonce=0):
    """获取Atomicals Payload的hex编码"""
    import binascii
    payload_bytes = get_atomicals_payload(op_type, time_val, nonce)
    return binascii.hexlify(payload_bytes).decode()

def calculate_inscription_amount():
    """计算需要发送到临时地址的金额"""
    return FEE_CONFIG["min_output"] + FEE_CONFIG["reveal_fee"]

def get_protocol_hex():
    """获取协议标识的hex编码"""
    return INSCRIPTION_CONFIG["protocol_hex"]

def get_op_type_hex():
    """获取操作类型的hex编码"""
    return INSCRIPTION_CONFIG["op_type_hex"]

if __name__ == "__main__":
    print("=== ARC-20/Atomicals配置信息 ===")
    print(f"网络: {NETWORK}")
    print(f"协议配置: {PROTOCOL_CONFIG}")
    print(f"inscription金额: {calculate_inscription_amount()} sats")
    print(f"费用配置: {FEE_CONFIG}")
    
    # 测试payload生成
    print(f"\n=== Payload测试 ===")
    payload_hex = get_atomicals_payload_hex("mint")
    print(f"Mint payload hex: {payload_hex}") 