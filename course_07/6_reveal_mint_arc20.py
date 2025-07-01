#!/usr/bin/env python3
"""
ARC-20/Atomicals MINT REVEAL交易创建
用途: 从临时地址reveal mint inscription到主地址 (带bitworkr挖矿功能)
前提: 必须先运行5_commit_mint_arc20.py并确认交易
"""

import time
import cbor2
import binascii
import struct
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

from arc20_config import (
    PRIVATE_KEY_WIF, NETWORK, FEE_CONFIG, PROTOCOL_CONFIG,
    get_atomicals_payload_hex, calculate_inscription_amount,
    INSCRIPTION_CONFIG, get_protocol_hex, get_op_type_hex
)

def load_arc20_commit_info():
    """从文件加载ARC-20 commit信息"""
    try:
        persistence_dir = os.path.join(os.path.dirname(__file__), "persistence")
        commit_file = os.path.join(persistence_dir, "commit_arc20_info.json")
        with open(commit_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 persistence/commit_arc20_info.json 文件")
        print("请先运行 5_commit_mint_arc20.py 创建ARC-20 MINT COMMIT交易")
        return None

def mine_reveal_transaction(private_key, commit_info, bitworkr_prefix):
    """
    挖矿生成满足bitworkr前缀的reveal交易
    
    Args:
        private_key: 私钥对象
        commit_info: commit信息
        bitworkr_prefix: 目标txid前缀
        
    Returns:
        tuple: (reveal_tx, inscription_script, time_val, nonce, payload_hex)
    """
    
    public_key = private_key.get_public_key()
    pubkey_xonly = public_key.to_x_only_hex()
    
    print(f"开始reveal挖矿，目标txid前缀: {bitworkr_prefix}")
    print(f"公钥: {pubkey_xonly}")
    
    # 从commit信息获取参数
    commit_txid = commit_info['commit_txid']
    temp_address = commit_info['temp_address']
    inscription_amount = commit_info['inscription_amount']
    
    # 使用commit时保存的时间戳和nonce（如果存在）
    if 'time' in commit_info and 'nonce' in commit_info:
        now = commit_info['time']
        nonce = commit_info['nonce']
        print(f"使用commit时的时间戳: {now}, nonce: {nonce}")
    else:
        # 如果没有保存，使用当前值
        now = int(time.time())
        nonce = 0
        print(f"使用当前时间戳: {now}, nonce: {nonce}")
    
    # 计算reveal输出金额
    reveal_fee = FEE_CONFIG['reveal_fee']
    output_amount = inscription_amount - reveal_fee
    
    if output_amount < FEE_CONFIG['min_output']:
        output_amount = FEE_CONFIG['min_output']
        reveal_fee = inscription_amount - output_amount
        print(f"调整费用: {reveal_fee} sats (确保输出 >= {FEE_CONFIG['min_output']} sats)")
    
    print(f"输入金额: {inscription_amount} sats")
    print(f"REVEAL费用: {reveal_fee} sats")
    print(f"输出金额: {output_amount} sats")
    
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
    
    # 重建inscription脚本（使用commit时保存的参数）
    protocol_hex = get_protocol_hex()
    op_type_hex = get_op_type_hex()
    
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
    
    # 验证临时地址
    temp_address_obj = public_key.get_taproot_address([[inscription_script]])
    
    print(f"\n=== 脚本验证 ===")
    print(f"计算的临时地址: {temp_address_obj.to_string()}")
    print(f"预期的临时地址: {temp_address}")
    
    if temp_address_obj.to_string() != temp_address:
        print("❌ 临时地址不匹配! 请检查inscription脚本")
        print("可能原因：时间戳或nonce与commit时不一致")
        return None, None, None, None, None
    
    print("✅ inscription脚本验证通过!")
    print(f"inscription脚本hex: {inscription_script.to_hex()}")
    
    # 创建基础reveal交易（不签名）
    tx_input = TxInput(commit_txid, 0)
    tx_output = TxOutput(output_amount, public_key.get_taproot_address().to_script_pub_key())
    
    reveal_tx = Transaction([tx_input], [tx_output], has_segwit=True)
    
    print(f"\n开始reveal挖矿，只改变sequence number...")
    
    # 开始挖矿 - 只改变sequence number（和commit一样的逻辑）
    start_time = time.time()
    sequence = 0xffffffff  # 从0xffffffff开始递减
    
    while sequence >= 0:  # 从0xffffffff开始递减
        # 重新创建TxInput对象，设置新的sequence
        new_tx_input = TxInput(commit_txid, 0)
        new_tx_input.sequence = struct.pack("<I", sequence)  # 4字节小端序
        
        # 重新创建Transaction
        reveal_tx = Transaction([new_tx_input], [tx_output], has_segwit=True)
        
        # 计算交易hash（不签名）
        txid = reveal_tx.get_txid()
        
        # 检查是否满足挖矿条件
        if txid.startswith(bitworkr_prefix):
            elapsed = time.time() - start_time
            print(f"✅ reveal挖矿成功!")
            print(f"  耗时: {elapsed:.2f}秒")
            print(f"  sequence: {sequence} (0x{sequence:08x})")
            print(f"  time: {now}")
            print(f"  nonce: {nonce}")
            print(f"  reveal txid: {txid}")
            print(f"  payload hex: {payload_hex}")
            
            # 现在签名交易
            try:
                # 关键: script path签名
                signature = private_key.sign_taproot_input(
                    reveal_tx,
                    0,
                    [temp_address_obj.to_script_pub_key()],
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
                    is_odd=temp_address_obj.is_odd()
                )
                
                print(f"✅ 控制块: {control_block.to_hex()}")
                print(f"parity bit: {temp_address_obj.is_odd()}")
                
                # 构建witness
                reveal_tx.witnesses.append(TxWitnessInput([
                    signature,
                    inscription_script.to_hex(),
                    control_block.to_hex()
                ]))
                
                print(f"✅ reveal交易签名成功!")
                print(f"TxID: {reveal_tx.get_txid()}")
                print(f"WTxID: {reveal_tx.get_wtxid()}")
                print(f"交易大小: {reveal_tx.get_size()} bytes")
                print(f"虚拟大小: {reveal_tx.get_vsize()} vbytes")
                print(f"最终sequence: {sequence} (0x{sequence:08x}) - BIP68兼容")
                
                return reveal_tx, inscription_script, now, nonce, payload_hex
                
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
    
    print("❌ reveal挖矿失败，未找到满足条件的sequence")
    return None, None, None, None, None

def create_mint_reveal_transaction():
    """
    创建ARC-20 MINT REVEAL交易 (带bitworkr挖矿)
    
    Returns:
        Transaction: 签名后的mint reveal交易
    """
    
    setup(NETWORK)
    
    print(f"=== 创建ARC-20/Atomicals MINT REVEAL交易 ===")
    
    # 加载commit信息
    commit_info = load_arc20_commit_info()
    if not commit_info:
        return None
    
    # 验证操作类型
    if commit_info.get("operation") != "arc20_mint":
        print("❌ commit_arc20_info.json 不是ARC-20 MINT操作的信息")
        return None
    
    print(f"ARC-20 MINT COMMIT TxID: {commit_info['commit_txid']}")
    print(f"临时地址: {commit_info['temp_address']}")
    print(f"主地址: {commit_info['key_path_address']}")
    print(f"inscription金额: {commit_info['inscription_amount']} sats")
    
    # 显示配置信息
    print(f"\n=== 配置信息 ===")
    print(f"协议: {commit_info['protocol']}")
    print(f"操作类型: {commit_info['op_type']}")
    print(f"代币符号: {commit_info['mint_ticker']}")
    print(f"bitworkc前缀: {commit_info['bitworkc']}")
    print(f"bitworkr前缀: {commit_info['bitworkr']}")
    
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
    
    # 挖矿生成reveal交易
    print(f"\n=== 开始reveal挖矿 ===")
    result = mine_reveal_transaction(private_key, commit_info, commit_info['bitworkr'])
    if not result:
        print("❌ reveal挖矿失败")
        return None
    
    reveal_tx, inscription_script, time_val, nonce, payload_hex = result
    
    print(f"\n=== 输出详情 ===")
    print(f"输出0: {reveal_tx.outputs[0].amount} sats -> {key_path_address.to_string()} (mint inscription + 代币)")
    
    return reveal_tx

def broadcast_mint_reveal(reveal_tx):
    """显示广播信息"""
    
    if not reveal_tx:
        print("❌ 没有有效的ARC-20 MINT REVEAL交易")
        return
    
    print(f"\n" + "="*60)
    print(f"🚀 ARC-20/Atomicals MINT REVEAL交易准备就绪!")
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
    print(f"- 获得ARC-20 inscription ID")
    print(f"- ARC-20代币MINT完成! 🎉")
    print(f"- 你的钱包将获得minted的ARC-20代币!")

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
    
    # 创建ARC-20 MINT REVEAL交易
    reveal_tx = create_mint_reveal_transaction()
    
    if reveal_tx:
        broadcast_mint_reveal(reveal_tx)
        
        print(f"\n💡 重要提醒:")
        print(f"- 确保ARC-20 MINT COMMIT交易已确认")
        print(f"- ARC-20 REVEAL成功后代币余额会增加")
        print(f"- 可以用Atomicals钱包查看代币余额")
        print(f"- 每次MINT都会消耗一次MINT机会")
    else:
        print(f"❌ ARC-20 MINT REVEAL交易创建失败")
