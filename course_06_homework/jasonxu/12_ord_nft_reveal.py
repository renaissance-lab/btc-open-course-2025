#!/usr/bin/env python3

from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.utils import ControlBlock
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey

# 导入工具模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

import json
import requests

import configparser
conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)


from utxo_scanner import select_best_utxo
from build_nft_script import build_nft_script
from brc20_config import (
    NETWORK, FEE_CONFIG, 
    calculate_inscription_amount,
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

def create_nft_commit_transaction():
    """
    创建COMMIT交易
    
    Returns:
        tuple: (commit_tx, temp_address, key_path_address)
    """
    
    setup(NETWORK)
    
    # 初始化密钥
    private_key = PrivateKey.from_wif(conf.get("testnet3", "private_key_wif"))
    public_key = private_key.get_public_key()
    key_path_address = public_key.get_taproot_address()  # 主地址
    
    print(f"公钥: {public_key.to_hex()}")
    print(f"x-only公钥: {public_key.to_x_only_hex()}")
    print(f"主地址: {key_path_address.to_string()}")
    
    # 选择UTXO
    inscription_amount = calculate_inscription_amount()
    min_utxo_amount = inscription_amount + FEE_CONFIG["commit_fee"] + 546  # 预留找零
    
    selected_utxo = select_best_utxo(key_path_address.to_string(), min_utxo_amount)
    if not selected_utxo:
        print(f"❌ 没有足够的UTXO支付 {min_utxo_amount} sats")
        return None, None, None
    
    # 创建inscription脚本
    inscription_script = [
        public_key.to_x_only_hex(),
        "OP_CHECKSIG"
        ]
    nft_script = build_nft_script("/home/jfxu/Downloads/good.jpeg")
    for item in nft_script:
        inscription_script.append(item)
    inscription_script = Script(inscription_script)
    
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

def create_nft_reveal_transaction():
    """
    创建REVEAL交易
    
    Returns:
        Transaction: 签名后的reveal交易
    """
    
    setup(NETWORK)
    
    # 加载commit信息
    commit_info = load_commit_info()
    if not commit_info:
        return None
    
    print(f"COMMIT TxID: {commit_info['commit_txid']}")
    print(f"临时地址: {commit_info['temp_address']}")
    print(f"主地址: {commit_info['key_path_address']}")
    print(f"inscription金额: {commit_info['inscription_amount']} sats")
    
    # 初始化密钥
    private_key = PrivateKey.from_wif(conf.get("testnet3", "private_key_wif"))
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
    inscription_script = [
        public_key.to_x_only_hex(),
        "OP_CHECKSIG"
        ]
    nft_script = build_nft_script("/home/jfxu/Downloads/good.jpeg")
    for item in nft_script:
        inscription_script.append(item)
    inscription_script = Script(inscription_script)
    
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

def broadcast_tx_by_mempoolspace(tx):
    if not tx:
        print("❌ 没有有效的COMMIT交易")
        return
    
    print("\n广播交易...")
    mempool_api = "https://mempool.space/testnet/api/tx"
    try:
        response = requests.post(mempool_api, data=tx)
        if response.status_code == 200:
            txid = response.text
            print(f"交易成功！")
            print(f"交易ID: {txid}")
            print(f"查看交易: https://mempool.space/testnet/tx/{txid}")
        else:
            print(f"广播失败: {response.text}")
    except Exception as e:
        print(f"错误: {e}")   


if __name__ == "__main__":

    reveal_tx = create_nft_reveal_transaction()
    signed_tx = reveal_tx.serialize()
    print("\n reveal transaction:\n" + signed_tx)
    broadcast_tx_by_mempoolspace(signed_tx)    