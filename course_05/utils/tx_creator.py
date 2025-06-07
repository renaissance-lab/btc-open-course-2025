from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
from typing import Tuple, List, Dict
from tools.utxo_scanner import get_utxos
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_taproot_tx(
    sender_private_key: str,
    recipient_addr: str,
    amount_to_send: float,
    fee_rate: float
) -> Tuple[str, dict]:
    """
    创建Taproot交易
    
    Args:
        sender_private_key: 发送方私钥
        recipient_addr: 接收方地址
        amount_to_send: 发送金额（BTC）
        fee_rate: 费率（sat/vB）
        
    Returns:
        Tuple[str, dict]: (签名后的交易十六进制字符串, 交易详情)
    """
    # 设置测试网
    setup('testnet')
    
    # 发送方信息
    sender_key = PrivateKey(sender_private_key)
    sender_pub = sender_key.get_public_key()
    sender_address = sender_pub.get_taproot_address()
    
    print("\n地址信息:")
    print("=" * 50)
    print(f"发送方地址: {sender_address.to_string()}")
    print(f"接收方地址: {recipient_addr}")
    print()
    
    # 接收方地址
    recipient_address = P2trAddress(recipient_addr)
    
    # 获取UTXO
    utxos = get_utxos(sender_address.to_string())
    
    # 计算总输入金额
    total_input = sum(utxo['value'] for utxo in utxos)
    amount_to_send_sats = to_satoshis(amount_to_send)
    
    print("\n金额信息（输入）:")
    print("=" * 50)
    print(f"总输入金额: {total_input} 聪 ({total_input/100000000:.8f} BTC)")
    print(f"计划发送: {amount_to_send_sats} 聪 ({amount_to_send:.8f} BTC)")
    print()
    
    # 创建输入
    tx_inputs = []
    input_amounts = []
    input_scripts = []
    
    for utxo in utxos:
        tx_inputs.append(TxInput(utxo['txid'], utxo['vout']))
        input_amounts.append(utxo['value'])
        input_scripts.append(sender_address.to_script_pub_key())
    
    # 第一次估算手续费（基于未签名交易）
    initial_tx = Transaction(
        tx_inputs,
        [
            TxOutput(amount_to_send_sats, recipient_address.to_script_pub_key()),
            TxOutput(0, sender_address.to_script_pub_key())
        ],
        has_segwit=True
    )
    initial_fee = int(initial_tx.get_vsize() * fee_rate)
    
    # 计算初始找零金额
    change_amount = total_input - amount_to_send_sats - initial_fee
    if change_amount <= 0:
        raise Exception("Insufficient funds for transaction and fee")
    
    # 创建完整交易
    tx_outputs = [
        TxOutput(amount_to_send_sats, recipient_address.to_script_pub_key()),
        TxOutput(change_amount, sender_address.to_script_pub_key())
    ]
    tx = Transaction(tx_inputs, tx_outputs, has_segwit=True)
    
    # 签名每个输入
    for i in range(len(tx_inputs)):
        sig = sender_key.sign_taproot_input(
            tx,
            i,
            input_scripts,
            input_amounts
        )
        tx.witnesses.append(TxWitnessInput([sig]))
    
    # 获取最终的虚拟大小和手续费
    final_vsize = tx.get_vsize()
    final_fee = int(final_vsize * fee_rate)
    
    # 如果最终手续费大于初始手续费，需要调整找零金额
    if final_fee > initial_fee:
        fee_difference = final_fee - initial_fee
        change_amount -= fee_difference
        if change_amount <= 0:
            raise Exception("Insufficient funds after fee adjustment")
        
        # 使用调整后的找零金额重新创建交易
        tx_outputs[1].amount = change_amount
        tx = Transaction(tx_inputs, tx_outputs, has_segwit=True)
        
        # 重新签名
        tx.witnesses = []
        for i in range(len(tx_inputs)):
            sig = sender_key.sign_taproot_input(
                tx,
                i,
                input_scripts,
                input_amounts
            )
            tx.witnesses.append(TxWitnessInput([sig]))
    
    print("\n费用计算详情:")
    print("=" * 50)
    print(f"初始虚拟大小: {initial_tx.get_vsize()} vbytes")
    print(f"最终虚拟大小: {final_vsize} vbytes")
    print(f"费率: {fee_rate} sat/vB")
    print(f"最终手续费: {final_fee} 聪 ({final_fee/100000000:.8f} BTC)")
    print()
    
    print("\n金额信息（输出）:")
    print("=" * 50)
    print(f"发送金额: {amount_to_send_sats} 聪 ({amount_to_send:.8f} BTC)")
    print(f"找零金额: {change_amount} 聪 ({change_amount/100000000:.8f} BTC)")
    print(f"手续费: {final_fee} 聪 ({final_fee/100000000:.8f} BTC)")
    print(f"总支出: {amount_to_send_sats + change_amount + final_fee} 聪")
    print()
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    # 准备交易详情
    tx_details = {
        "from_address": sender_address.to_string(),
        "to_address": recipient_addr,
        "amount": amount_to_send,
        "amount_sats": amount_to_send_sats,
        "change_amount": change_amount / 100000000,
        "change_amount_sats": change_amount,
        "fee": final_fee / 100000000,
        "fee_sats": final_fee,
        "tx_size": tx.get_size(),
        "tx_vsize": tx.get_vsize(),
        "txid": tx.get_txid()
    }
    
    return signed_tx, tx_details 