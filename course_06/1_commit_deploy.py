#!/usr/bin/env python3
"""
BRC-20 COMMIT交易创建
用途: 将funds发送到临时地址，准备inscription



"""

from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey

# 导入工具模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from utxo_scanner import select_best_utxo
from brc20_config import (
    PRIVATE_KEY_WIF, NETWORK, FEE_CONFIG, 
    get_brc20_hex, calculate_inscription_amount,
    INSCRIPTION_CONFIG
)

def create_commit_transaction(op_type="deploy"):
    """
    创建COMMIT交易
    
    Args:
        op_type: 操作类型 ("deploy" 或 "mint")
    
    Returns:
        tuple: (commit_tx, temp_address, key_path_address)
    """
    
    setup(NETWORK)
    
    print(f"=== 创建BRC-20 {op_type.upper()} COMMIT交易 ===")
    
    # 初始化密钥
    private_key = PrivateKey.from_wif(PRIVATE_KEY_WIF)
    public_key = private_key.get_public_key()
    key_path_address = public_key.get_taproot_address()  # 主地址
    
    # print(f"私钥WIF: {PRIVATE_KEY_WIF}")
    print(f"公钥: {public_key.to_hex()}")
    print(f"x-only公钥: {public_key.to_x_only_hex()}")
    print(f"主地址: {key_path_address.to_string()}")
    
    # 选择UTXO
    inscription_amount = calculate_inscription_amount()
    min_utxo_amount = inscription_amount + FEE_CONFIG["commit_fee"] + 546  # 预留找零
    
    selected_utxo = select_best_utxo(min_utxo_amount)
    if not selected_utxo:
        print(f"❌ 没有足够的UTXO支付 {min_utxo_amount} sats")
        return None, None, None
    
    # 创建inscription脚本
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
    
    # 创建临时地址
    temp_address = public_key.get_taproot_address([[inscription_script]])
    
    print(f"\n=== 地址验证 ===")
    print(f"临时地址: {temp_address.to_string()}")
    print(f"脚本hex: {inscription_script.to_hex()}")
    
    # 计算金额
    utxo_amount = selected_utxo["amount"]
    commit_fee = FEE_CONFIG["commit_fee"]
    change_amount = utxo_amount - inscription_amount - commit_fee
    
    print(f"\n=== 金额计算 ===")
    print(f"UTXO金额: {utxo_amount} sats")
    print(f"inscription金额: {inscription_amount} sats")
    print(f"COMMIT费用: {commit_fee} sats")
    print(f"找零金额: {change_amount} sats")
    
    if change_amount < 0:
        print(f"❌ 金额不足! 需要至少 {inscription_amount + commit_fee} sats")
        return None, None, None
    
    if change_amount < 546 and change_amount > 0:
        print(f"⚠️  找零太小({change_amount} sats)，将被合并到手续费中")
        commit_fee += change_amount
        change_amount = 0
    
    # 创建交易
    print(f"\n=== 构建COMMIT交易 ===")
    
    tx_input = TxInput(selected_utxo["txid"], selected_utxo["vout"])
    
    outputs = [
        TxOutput(inscription_amount, temp_address.to_script_pub_key())
    ]
    
    # 如果有找零，添加找零输出
    if change_amount > 0:
        outputs.append(TxOutput(change_amount, key_path_address.to_script_pub_key()))
    
    commit_tx = Transaction([tx_input], outputs, has_segwit=True)
    
    # 签名交易
    try:
        signature = private_key.sign_taproot_input(
            commit_tx,
            0,
            [key_path_address.to_script_pub_key()],
            [utxo_amount]
        )
        
        commit_tx.witnesses.append(TxWitnessInput([signature]))
        
        print(f"✅ COMMIT交易签名成功!")
        print(f"TxID: {commit_tx.get_txid()}")
        print(f"交易大小: {commit_tx.get_size()} bytes")
        print(f"虚拟大小: {commit_tx.get_vsize()} vbytes")
        
        print(f"\n=== 输出详情 ===")
        print(f"输出0: {inscription_amount} sats -> {temp_address.to_string()} (临时地址)")
        if change_amount > 0:
            print(f"输出1: {change_amount} sats -> {key_path_address.to_string()} (找零)")
        
        return commit_tx, temp_address, key_path_address
        
    except Exception as e:
        print(f"❌ 签名失败: {e}")
        return None, None, None

def broadcast_commit(commit_tx):
    """显示广播信息"""
    
    if not commit_tx:
        print("❌ 没有有效的COMMIT交易")
        return
    
    print(f"\n" + "="*60)
    print(f"🚀 COMMIT交易准备就绪!")
    print(f"="*60)
    
    print(f"交易hex: {commit_tx.serialize()}")
    print(f"")
    print(f"广播命令:")
    print(f"bitcoin-cli -{NETWORK} sendrawtransaction {commit_tx.serialize()}")
    print(f"")
    print(f"在线广播:")
    print(f"https://live.blockcypher.com/btc-{NETWORK}/pushtx/")
    print(f"https://blockstream.info/{NETWORK}/tx/push")
    print(f"")
    print(f"⚠️  广播后请等待确认，然后运行 2_reveal.py")

if __name__ == "__main__":
    # 创建COMMIT交易 (默认deploy操作)
    commit_tx, temp_address, key_path_address = create_commit_transaction("deploy")
    
    if commit_tx:
        # 保存关键信息到文件，供reveal使用
        commit_info = {
            "commit_txid": commit_tx.get_txid(),
            "temp_address": temp_address.to_string(),
            "key_path_address": key_path_address.to_string(),
            "inscription_amount": calculate_inscription_amount()
        }
        
        import json
        with open("commit_info.json", "w") as f:
            json.dump(commit_info, f, indent=2)
        
        print(f"\n💾 信息已保存到 commit_info.json")
        
        # 显示广播信息
        broadcast_commit(commit_tx)
    else:
        print(f"❌ COMMIT交易创建失败")