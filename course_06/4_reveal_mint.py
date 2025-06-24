#!/usr/bin/env python3
"""
BRC-20 MINT REVEAL交易创建
用途: 从临时地址reveal mint inscription到主地址
前提: 必须先运行1_commit_mint.py并确认交易
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
    get_brc20_hex, INSCRIPTION_CONFIG, get_brc20_json
)

def load_mint_commit_info():
    """从文件加载mint commit信息"""
    try:
        with open("commit_mint_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 commit_mint_info.json 文件")
        print("请先运行 1_commit_mint.py 创建MINT COMMIT交易")
        return None

def create_mint_reveal_transaction():
    """
    创建MINT REVEAL交易
    
    Returns:
        Transaction: 签名后的mint reveal交易
    """
    
    setup(NETWORK)
    
    print(f"=== 创建BRC-20 MINT REVEAL交易 ===")
    
    # 加载commit信息
    commit_info = load_mint_commit_info()
    if not commit_info:
        return None
    
    # 验证操作类型
    if commit_info.get("operation") != "mint":
        print("❌ commit_mint_info.json 不是MINT操作的信息")
        return None
    
    print(f"MINT COMMIT TxID: {commit_info['commit_txid']}")
    print(f"临时地址: {commit_info['temp_address']}")
    print(f"主地址: {commit_info['key_path_address']}")
    print(f"inscription金额: {commit_info['inscription_amount']} sats")
    
    # 显示MINT信息
    mint_json = get_brc20_json("mint")
    print(f"MINT数据: {mint_json}")
    
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
    
    # 重建MINT inscription脚本
    brc20_hex = get_brc20_hex("mint")
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
        print("❌ 临时地址不匹配! 请检查MINT脚本")
        return None
    
    print("✅ MINT脚本验证通过!")
    print(f"MINT脚本hex: {inscription_script.to_hex()}")
    
    # 计算reveal输出金额
    inscription_amount = commit_info['inscription_amount']
    reveal_fee = FEE_CONFIG['reveal_fee']
    output_amount = inscription_amount - reveal_fee
    
    print(f"\n=== MINT REVEAL金额计算 ===")
    print(f"输入金额: {inscription_amount} sats")
    print(f"REVEAL费用: {reveal_fee} sats")
    print(f"输出金额: {output_amount} sats")
    
    if output_amount < FEE_CONFIG['min_output']:
        output_amount = FEE_CONFIG['min_output']
        reveal_fee = inscription_amount - output_amount
        print(f"调整费用: {reveal_fee} sats (确保输出 >= {FEE_CONFIG['min_output']} sats)")
    
    # 创建交易
    print(f"\n=== 构建MINT REVEAL交易 ===")
    
    tx_input = TxInput(commit_info['commit_txid'], 0)
    tx_output = TxOutput(output_amount, key_path_address.to_script_pub_key())
    
    reveal_tx = Transaction([tx_input], [tx_output], has_segwit=True)
    
    print(f"未签名MINT REVEAL交易: {reveal_tx.serialize()}")
    
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
        
        print(f"\n✅ MINT REVEAL交易签名成功!")
        print(f"TxID: {reveal_tx.get_txid()}")
        print(f"WTxID: {reveal_tx.get_wtxid()}")
        print(f"交易大小: {reveal_tx.get_size()} bytes")
        print(f"虚拟大小: {reveal_tx.get_vsize()} vbytes")
        
        print(f"\n=== 输出详情 ===")
        print(f"输出0: {output_amount} sats -> {key_path_address.to_string()} (mint inscription + 代币)")
        
        return reveal_tx
        
    except Exception as e:
        print(f"❌ 签名失败: {e}")
        return None

def broadcast_mint_reveal(reveal_tx):
    """显示广播信息"""
    
    if not reveal_tx:
        print("❌ 没有有效的MINT REVEAL交易")
        return
    
    print(f"\n" + "="*60)
    print(f"🚀 MINT REVEAL交易准备就绪!")
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
    print(f"- 获得MINT inscription ID")
    print(f"- BRC-20代币MINT完成! 🎉")
    print(f"- 你的钱包将获得minted的代币!")

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
    
    # 创建MINT REVEAL交易
    reveal_tx = create_mint_reveal_transaction()
    
    if reveal_tx:
        broadcast_mint_reveal(reveal_tx)
        
        print(f"\n💡 重要提醒:")
        print(f"- 确保MINT COMMIT交易已确认")
        print(f"- MINT REVEAL成功后代币余额会增加")
        print(f"- 可以用UniSat等钱包查看代币余额")
        print(f"- 每次MINT都会消耗一次MINT机会")
    else:
        print(f"❌ MINT REVEAL交易创建失败")