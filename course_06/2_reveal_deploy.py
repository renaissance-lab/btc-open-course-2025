#!/usr/bin/env python3
"""
BRC-20 REVEAL交易创建
用途: 从临时地址reveal inscription到主地址
前提: 必须先运行1_commit.py并确认交易
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey

# 导入工具模块
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from brc20_config import (
    PRIVATE_KEY_WIF, NETWORK, FEE_CONFIG,
    get_brc20_hex, INSCRIPTION_CONFIG
)

def load_commit_info():
    """从文件加载commit信息"""
    try:
        with open("commit_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 commit_info.json 文件")
        print("请先运行 1_commit.py 创建COMMIT交易")
        return None

def create_reveal_transaction(op_type="deploy"):
    """
    创建REVEAL交易
    
    Args:
        op_type: 操作类型 ("deploy" 或 "mint")
    
    Returns:
        Transaction: 签名后的reveal交易
    """
    
    setup(NETWORK)
    
    print(f"=== 创建BRC-20 {op_type.upper()} REVEAL交易 ===")
    
    # 加载commit信息
    commit_info = load_commit_info()
    if not commit_info:
        return None
    
    print(f"COMMIT TxID: {commit_info['commit_txid']}")
    print(f"临时地址: {commit_info['temp_address']}")
    print(f"主地址: {commit_info['key_path_address']}")
    print(f"inscription金额: {commit_info['inscription_amount']} sats")
    
    # 初始化密钥
    private_key = PrivateKey.from_wif(PRIVATE_KEY_WIF)
    public_key = private_key.get_public_key()
    key_path_address = public_key.get_taproot_address()
    
    print(f"\n=== 地址验证 ===")
    print(f"计算的主地址: {key_path_address.to_string()}")
    print(f"预期的主地址: {commit_info['key_path_address']}")
    
    if key_path_address.to_string() != commit_info['key_path_address']:
        print("❌ 地址不匹配! 请检查私钥")
        return None
    
    print("✅ 地址验证通过!")
    
    # 重建inscription脚本
    brc20_hex = get_brc20_hex(op_type)
    inscription_script = Script([
        public_key.to_x_only_hex(),
        "OP_CHECKSIG", 
        "OP_0",
        "OP_IF",
        INSCRIPTION_CONFIG["ord_marker"],
        "OP_1",
        INSCRIPTION_CONFIG["content_type_hex"],
        "OP_0",
        brc20_hex,
        "OP_ENDIF"
    ])
    
    # 验证临时地址
    temp_address = public_key.get_taproot_address([[inscription_script]])
    
    print(f"\n=== 脚本验证 ===")
    print(f"计算的临时地址: {temp_address.to_string()}")
    print(f"预期的临时地址: {commit_info['temp_address']}")
    
    if temp_address.to_string() != commit_info['temp_address']:
        print("❌ 临时地址不匹配! 请检查脚本")
        return None
    
    print("✅ 脚本验证通过!")
    print(f"脚本hex: {inscription_script.to_hex()}")
    
    # 计算reveal输出金额
    inscription_amount = commit_info['inscription_amount']
    reveal_fee = FEE_CONFIG['reveal_fee']
    output_amount = inscription_amount - reveal_fee
    
    print(f"\n=== REVEAL金额计算 ===")
    print(f"输入金额: {inscription_amount} sats")
    print(f"REVEAL费用: {reveal_fee} sats")
    print(f"输出金额: {output_amount} sats")
    
    if output_amount < FEE_CONFIG['min_output']:
        output_amount = FEE_CONFIG['min_output']
        reveal_fee = inscription_amount - output_amount
        print(f"调整费用: {reveal_fee} sats (确保输出 >= {FEE_CONFIG['min_output']} sats)")
    
    # 创建交易
    print(f"\n=== 构建REVEAL交易 ===")
    
    tx_input = TxInput(commit_info['commit_txid'], 0)
    tx_output = TxOutput(output_amount, key_path_address.to_script_pub_key())
    
    reveal_tx = Transaction([tx_input], [tx_output], has_segwit=True)
    
    print(f"未签名交易: {reveal_tx.serialize()}")
    
    # 签名交易
    try:
        # 关键: script path签名
        signature = private_key.sign_taproot_input(
            reveal_tx,
            0,
            [temp_address.to_script_pub_key()],
            [inscription_amount],
            script_path=True,
            tapleaf_script=inscription_script,
            tweak=False
        )
        
        print(f"✅ 签名成功: {signature}")
        
        # 创建控制块
        control_block = ControlBlock(
            public_key,
            scripts=[inscription_script],
            index=0,
            is_odd=temp_address.is_odd()
        )
        
        print(f"✅ 控制块: {control_block.to_hex()}")
        print(f"parity bit: {temp_address.is_odd()}")
        
        # 构建witness
        reveal_tx.witnesses.append(TxWitnessInput([
            signature,
            inscription_script.to_hex(),
            control_block.to_hex()
        ]))
        
        print(f"\n✅ REVEAL交易签名成功!")
        print(f"TxID: {reveal_tx.get_txid()}")
        print(f"WTxID: {reveal_tx.get_wtxid()}")
        print(f"交易大小: {reveal_tx.get_size()} bytes")
        print(f"虚拟大小: {reveal_tx.get_vsize()} vbytes")
        
        print(f"\n=== 输出详情 ===")
        print(f"输出0: {output_amount} sats -> {key_path_address.to_string()} (inscription + 代币)")
        
        return reveal_tx
        
    except Exception as e:
        print(f"❌ 签名失败: {e}")
        return None

def broadcast_reveal(reveal_tx):
    """显示广播信息"""
    
    if not reveal_tx:
        print("❌ 没有有效的REVEAL交易")
        return
    
    print(f"\n" + "="*60)
    print(f"🚀 REVEAL交易准备就绪!")
    print(f"="*60)
    
    print(f"交易hex: {reveal_tx.serialize()}")
    print(f"")
    print(f"广播命令:")
    print(f"bitcoin-cli -{NETWORK} sendrawtransaction {reveal_tx.serialize()}")
    print(f"")
    print(f"在线广播:")
    print(f"https://live.blockcypher.com/btc-{NETWORK}/pushtx/")
    print(f"https://blockstream.info/{NETWORK}/tx/push")
    print(f"")
    print(f"期望结果:")
    print(f"- 交易被网络接受")
    print(f"- 获得inscription ID")
    print(f"- BRC-20代币操作完成! 🎉")

def check_dependencies():
    """检查依赖"""
    try:
        from bitcoinutils.utils import ControlBlock
        print("✅ ControlBlock类可用")
        return True
    except ImportError:
        print("❌ ControlBlock类不可用")
        print("请更新bitcoinutils: pip install --upgrade bitcoin-utils")
        return False

if __name__ == "__main__":
    # 检查依赖
    if not check_dependencies():
        exit(1)
    
    # 创建REVEAL交易 (默认deploy操作)
    reveal_tx = create_reveal_transaction("deploy")
    
    if reveal_tx:
        broadcast_reveal(reveal_tx)
        
        print(f"\n💡 重要提醒:")
        print(f"- 确保COMMIT交易已确认")
        print(f"- REVEAL成功后inscription即生效")
        print(f"- 可以用区块链浏览器验证结果")
    else:
        print(f"❌ REVEAL交易创建失败")