#!/usr/bin/env python3
"""
ARC-20/Atomicals MINT COMMIT交易创建
用途: 为MINT操作将funds发送到临时地址，准备inscription (带挖矿功能)
"""

import time
import cbor2
import binascii
from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
import struct

# 导入工具模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from utxo_scanner import select_best_utxo
from arc20_config import (
    PRIVATE_KEY_WIF, NETWORK, FEE_CONFIG, PROTOCOL_CONFIG,
    get_atomicals_payload_hex, calculate_inscription_amount,
    INSCRIPTION_CONFIG, get_protocol_hex, get_op_type_hex
)

def mine_commit_address(private_key, bitworkc_prefix):
    """
    挖矿生成满足bitworkc前缀的commit交易
    
    Args:
        private_key: 私钥对象
        bitworkc_prefix: 目标txid前缀
        
    Returns:
        tuple: (temp_address, inscription_script, time_val, nonce, payload_hex, commit_tx)
    """
    
    public_key = private_key.get_public_key()
    pubkey_xonly = public_key.to_x_only_hex()
    
    print(f"开始挖矿，目标txid前缀: {bitworkc_prefix}")
    print(f"公钥: {pubkey_xonly}")
    
    # 预计算固定部分
    protocol_hex = get_protocol_hex()
    op_type_hex = get_op_type_hex()
    
    # 获取真实UTXO
    inscription_amount = calculate_inscription_amount()
    commit_fee = FEE_CONFIG["commit_fee"]
    min_utxo_amount = inscription_amount + commit_fee + 546  # 预留找零
    
    selected_utxo = select_best_utxo(min_utxo_amount)
    if not selected_utxo:
        print(f"❌ 没有足够的UTXO支付 {min_utxo_amount} sats")
        return None, None, None, None, None, None
    
    print(f"✅ 选择UTXO: {selected_utxo['txid']}:{selected_utxo['vout']} ({selected_utxo['amount']} sats)")
    
    # 固定时间戳和nonce，用于生成临时地址
    now = int(time.time())
    nonce = 0
    
    # 生成payload
    payload = {
        "args": {
            "time": now,
            "nonce": nonce,
            "bitworkc": PROTOCOL_CONFIG["bitworkc"],
            "bitworkr": PROTOCOL_CONFIG["bitworkr"],
            "mint_ticker": PROTOCOL_CONFIG["mint_ticker"]
        }
    }
    payload_bytes = cbor2.dumps(payload)
    payload_hex = binascii.hexlify(payload_bytes).decode()
    
    # 创建inscription脚本
    inscription_script = Script([
        pubkey_xonly,
        "OP_CHECKSIG",
        "OP_0",
        "OP_IF",
        protocol_hex,            # "atom"
        op_type_hex,             # "dmt"
        payload_hex,             # CBOR编码的payload
        "OP_ENDIF"
    ])
    
    # 生成临时地址
    temp_address = public_key.get_taproot_address([[inscription_script]])
    
    # 创建基础commit交易（不签名）
    tx_input = TxInput(selected_utxo["txid"], selected_utxo["vout"])
    tx_output = TxOutput(inscription_amount, temp_address.to_script_pub_key())
    
    commit_tx = Transaction([tx_input], [tx_output], has_segwit=True)
    
    print(f"临时地址: {temp_address.to_string()}")
    print(f"开始挖矿，只改变sequence number...")
    
    # 开始挖矿 - 只改变sequence number
    start_time = time.time()
    sequence = 0xffffffff  # 直接使用BIP68兼容的sequence
    
    while sequence >= 0:  # 从0xffffffff开始递减
        # 重新创建TxInput对象，设置新的sequence
        new_tx_input = TxInput(selected_utxo["txid"], selected_utxo["vout"])
        new_tx_input.sequence = struct.pack("<I", sequence)  # 4字节小端序
        
        # 重新创建Transaction
        commit_tx = Transaction([new_tx_input], [tx_output], has_segwit=True)
        
        # 计算交易hash（不签名）
        txid = commit_tx.get_txid()
        
        # 检查是否满足挖矿条件
        if txid.startswith(bitworkc_prefix):
            elapsed = time.time() - start_time
            print(f"✅ 挖矿成功!")
            print(f"  耗时: {elapsed:.2f}秒")
            print(f"  sequence: {sequence} (0x{sequence:08x})")
            print(f"  time: {now}")
            print(f"  nonce: {nonce}")
            print(f"  临时地址: {temp_address.to_string()}")
            print(f"  commit txid: {txid}")
            print(f"  payload hex: {payload_hex}")
            print(f"  脚本 hex: {inscription_script.to_hex()}")
            
            # 现在签名交易
            try:
                signature = private_key.sign_taproot_input(
                    commit_tx,
                    0,
                    [public_key.get_taproot_address().to_script_pub_key()],
                    [selected_utxo["amount"]]
                )
                commit_tx.witnesses.append(TxWitnessInput([signature]))
                print(f"✅ 交易签名成功!")
                print(f"最终TxID: {commit_tx.get_txid()}")
                print(f"最终sequence: {sequence} (0x{sequence:08x}) - BIP68兼容")
                
                return temp_address, inscription_script, now, nonce, payload_hex, commit_tx
                
            except Exception as e:
                print(f"❌ 签名失败: {e}")
                sequence -= 1
                continue
        
        sequence -= 1
        
        # 每10000次显示进度
        if sequence % 10000 == 0:
            elapsed = time.time() - start_time
            rate = (0xffffffff - sequence) / elapsed if elapsed > 0 else 0
            print(f"已尝试 {0xffffffff - sequence} 次, 耗时 {elapsed:.1f}s, 速率 {rate:.0f} hash/s, 当前txid: {txid}")
    
    print("❌ 挖矿失败，未找到满足条件的sequence")
    return None, None, None, None, None, None

def create_mint_commit_transaction():
    """
    创建ARC-20 MINT COMMIT交易 (带挖矿)
    
    Returns:
        tuple: (commit_tx, temp_address, key_path_address)
    """
    
    setup(NETWORK)
    
    print(f"=== 创建ARC-20/Atomicals MINT COMMIT交易 ===")
    
    # 显示配置信息
    print(f"协议: {PROTOCOL_CONFIG['protocol']}")
    print(f"操作类型: {PROTOCOL_CONFIG['op_type']}")
    print(f"代币符号: {PROTOCOL_CONFIG['mint_ticker']}")
    print(f"bitworkc前缀: {PROTOCOL_CONFIG['bitworkc']}")
    print(f"bitworkr前缀: {PROTOCOL_CONFIG['bitworkr']}")
    
    # 初始化密钥
    private_key = PrivateKey.from_wif(PRIVATE_KEY_WIF)
    public_key = private_key.get_public_key()
    key_path_address = public_key.get_taproot_address()  # 主地址
    
    print(f"\n=== 密钥信息 ===")
    print(f"私钥WIF: {PRIVATE_KEY_WIF}")
    print(f"公钥: {public_key.to_hex()}")
    print(f"x-only公钥: {public_key.to_x_only_hex()}")
    print(f"主地址: {key_path_address.to_string()}")
    
    # 挖矿生成临时地址和commit交易
    print(f"\n=== 开始挖矿 ===")
    result = mine_commit_address(private_key, PROTOCOL_CONFIG['bitworkc'])
    if not result:
        print("❌ 挖矿失败")
        return None, None, None
    
    temp_address, inscription_script, time_val, nonce, payload_hex, commit_tx = result
    
    print(f"\n=== 地址验证 ===")
    print(f"临时地址: {temp_address.to_string()}")
    print(f"inscription脚本hex: {inscription_script.to_hex()}")
    print(f"Commit TxID: {commit_tx.get_txid()}")
    
    # 保存关键信息到文件，供reveal使用
    commit_info = {
        "commit_txid": commit_tx.get_txid(),
        "temp_address": temp_address.to_string(),
        "key_path_address": key_path_address.to_string(),
        "inscription_amount": calculate_inscription_amount(),
        "operation": "arc20_mint",
        "protocol": PROTOCOL_CONFIG["protocol"],
        "op_type": PROTOCOL_CONFIG["op_type"],
        "mint_ticker": PROTOCOL_CONFIG["mint_ticker"],
        "bitworkc": PROTOCOL_CONFIG["bitworkc"],
        "bitworkr": PROTOCOL_CONFIG["bitworkr"],
        "time": time_val,
        "nonce": nonce,
        "payload_hex": payload_hex
    }
    
    # 确保persistence目录存在
    persistence_dir = os.path.join(os.path.dirname(__file__), "persistence")
    os.makedirs(persistence_dir, exist_ok=True)
    
    import json
    with open(os.path.join(persistence_dir, "commit_arc20_info.json"), "w") as f:
        json.dump(commit_info, f, indent=2)
    
    print(f"\n💾 ARC-20信息已保存到 {os.path.join(persistence_dir, 'commit_arc20_info.json')}")
    
    # 显示广播信息
    broadcast_mint_commit(commit_tx)
    
    return commit_tx, temp_address, key_path_address

def broadcast_mint_commit(commit_tx):
    """显示广播信息"""
    
    if not commit_tx:
        print("❌ 没有有效的ARC-20 MINT COMMIT交易")
        return
    
    print(f"\n" + "="*60)
    print(f"🚀 ARC-20/Atomicals MINT COMMIT交易准备就绪!")
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
    print(f"⚠️  广播后请等待确认，然后运行 6_reveal_mint_arc20.py")

if __name__ == "__main__":
    # 创建ARC-20 MINT COMMIT交易
    commit_tx, temp_address, key_path_address = create_mint_commit_transaction()
    
    if commit_tx:
        # 读取刚才create_mint_commit_transaction里已经生成的commit_info
        # 或者直接在create_mint_commit_transaction里保存一次即可
        print(f"\n💾 ARC-20信息已保存到 {os.path.join(os.path.dirname(__file__), 'persistence', 'commit_arc20_info.json')}")
        # 显示广播信息
        broadcast_mint_commit(commit_tx)
    else:
        print(f"❌ ARC-20 MINT COMMIT交易创建失败")