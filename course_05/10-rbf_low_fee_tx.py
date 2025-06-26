from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
from tools.utxo_scanner import get_utxos
from typing import Tuple, List, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_rbf_tx(
    sender_private_key: str,
    recipient_addr: str,
    amount_to_send: float,
    fee_rate: float,
    enable_rbf: bool = True
) -> Tuple[str, dict]:
    """
    创建支持RBF的交易
    
    Args:
        sender_private_key: 发送方私钥
        recipient_addr: 接收方地址
        amount_to_send: 发送金额（BTC）
        fee_rate: 费率（sat/vB）
        enable_rbf: 是否启用RBF
        
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
        # 如果启用RBF，设置nSequence为0xfffffffe
        sequence = (0xfffffffe if enable_rbf else 0xffffffff).to_bytes(4, byteorder='little')
        tx_input = TxInput(utxo['txid'], utxo['vout'], sequence=sequence)
        tx_inputs.append(tx_input)
        input_amounts.append(utxo['value'])
        input_scripts.append(sender_address.to_script_pub_key())
    
    # 创建一个初始交易来估算大小
    initial_tx = Transaction(
        tx_inputs,
        [
            TxOutput(amount_to_send_sats, recipient_address.to_script_pub_key()),
            TxOutput(0, sender_address.to_script_pub_key())
        ],
        has_segwit=True
    )
    
    # 估算手续费
    estimated_vsize = initial_tx.get_vsize()
    min_fee_rate = 1.2  # 设置稍高于1 sat/vB的最小费率
    min_fee = int(estimated_vsize * min_fee_rate)
    
    # 确保手续费不低于预计的最小值
    fee = max(int(estimated_vsize * fee_rate), min_fee)
    
    # 计算找零金额
    change_amount = total_input - amount_to_send_sats - fee
    if change_amount <= 0:
        raise Exception(f"资金不足。需要 {amount_to_send_sats + fee} 聪，但只有 {total_input} 聪")
    
    # 检查找零是否满足dust限制（一般是330聪）
    if change_amount < 330:
        # 如果找零太少，就把它加到手续费中
        fee += change_amount
        change_amount = 0
        logger.info(f"找零金额低于dust限制，将找零 {change_amount} 聪添加到手续费中")
    
    # 创建最终输出
    tx_outputs = [
        TxOutput(amount_to_send_sats, recipient_address.to_script_pub_key()),
        TxOutput(change_amount, sender_address.to_script_pub_key())
    ]
    
    # 创建交易
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
        "fee": fee / 100000000,
        "fee_sats": fee,
        "fee_rate": fee_rate,
        "tx_size": tx.get_size(),
        "tx_vsize": tx.get_vsize(),
        "txid": tx.get_txid(),
        "rbf_enabled": enable_rbf,
        "input_utxos": [{"txid": utxo['txid'], "vout": utxo['vout'], "amount": utxo['value']} for utxo in utxos]
    }
    
    return signed_tx, tx_details

def compare_sequence_txid(
    sender_private_key: str,
    recipient_addr: str,
    amount_to_send: float,
    fee_rate: float
):
    setup('testnet')
    sender_key = PrivateKey(sender_private_key)
    sender_pub = sender_key.get_public_key()
    sender_address = sender_pub.get_taproot_address()
    recipient_address = P2trAddress(recipient_addr)
    utxos = get_utxos(sender_address.to_string())
    total_input = sum(utxo['value'] for utxo in utxos)
    amount_to_send_sats = to_satoshis(amount_to_send)
    fee = int(180 * fee_rate)  # 简单估算手续费
    change_amount = total_input - amount_to_send_sats - fee
    if change_amount < 0:
        raise Exception("资金不足")
    tx_inputs1 = []
    tx_inputs2 = []
    input_amounts = []
    input_scripts = []
    for utxo in utxos:
        tx_inputs1.append(TxInput(utxo['txid'], utxo['vout'], sequence=(0xffffffff).to_bytes(4, 'little')))
        tx_inputs2.append(TxInput(utxo['txid'], utxo['vout'], sequence=(0xfffffffe).to_bytes(4, 'little')))
        input_amounts.append(utxo['value'])
        input_scripts.append(sender_address.to_script_pub_key())
    tx_outputs = [
        TxOutput(amount_to_send_sats, recipient_address.to_script_pub_key()),
        TxOutput(change_amount, sender_address.to_script_pub_key())
    ]
    # 默认nSequence交易
    tx1 = Transaction(tx_inputs1, tx_outputs, has_segwit=True)
    # RBF nSequence交易
    tx2 = Transaction(tx_inputs2, tx_outputs, has_segwit=True)
    # 签名
    for i in range(len(tx_inputs1)):
        sig1 = sender_key.sign_taproot_input(tx1, i, input_scripts, input_amounts)
        sig2 = sender_key.sign_taproot_input(tx2, i, input_scripts, input_amounts)
        tx1.witnesses.append(TxWitnessInput([sig1]))
        tx2.witnesses.append(TxWitnessInput([sig2]))
    print("\n=== nSequence = 0xffffffff (默认, 不支持RBF) ===")
    print("txid:", tx1.get_txid())
    print("raw tx:", tx1.serialize())
    print("\n=== nSequence = 0xfffffffe (支持RBF) ===")
    print("txid:", tx2.get_txid())
    print("raw tx:", tx2.serialize())
    print("\n你会发现，仅仅nSequence的微小变化，txid就完全不同。")

def main():
    # 交易参数
    sender_private_key = "cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT"
    recipient_addr = "tb1pezpnfztmzltyvke55cwqc206vdyz8chz4w52yrd8w4ah402jqu2qv9hdkg"
    amount_to_send = 0.00001000  # 发送1000聪
    fee_rate = 1.0  # 低费率，1 sat/vB
    
    try:
        # 创建交易
        signed_tx, tx_details = create_rbf_tx(
            sender_private_key=sender_private_key,
            recipient_addr=recipient_addr,
            amount_to_send=amount_to_send,
            fee_rate=fee_rate,
            enable_rbf=True  # 启用RBF
        )
        
        # 打印交易信息
        print("\n低费率交易详情 (支持RBF):")
        print("=" * 50)
        print(f"交易ID: {tx_details['txid']}")
        print(f"交易大小: {tx_details['tx_size']} bytes")
        print(f"虚拟大小: {tx_details['tx_vsize']} vbytes")
        print("\n金额详情:")
        print(f"发送金额: {tx_details['amount_sats']} 聪 ({tx_details['amount']:.8f} BTC)")
        print(f"找零金额: {tx_details['change_amount_sats']} 聪 ({tx_details['change_amount']:.8f} BTC)")
        print(f"手续费: {tx_details['fee_sats']} 聪 ({tx_details['fee']:.8f} BTC)")
        print(f"费率: {tx_details['fee_rate']} sat/vB")
        print(f"RBF: {'已启用' if tx_details['rbf_enabled'] else '未启用'}")
        print("\n签名后的交易:")
        print(signed_tx)
        print("\n请先广播这笔低费率交易:")
        print("https://mempool.space/testnet/tx/push")
        print("\n如果交易确认太慢，可以使用RBF功能广播一笔更高手续费的交易。")
        print("\n重要信息 - 请保存用于RBF:")
        print("=" * 50)
        print("输入UTXO:")
        for i, utxo in enumerate(tx_details['input_utxos'], 1):
            print(f"UTXO #{i}:")
            print(f"  交易ID: {utxo['txid']}")
            print(f"  输出索引: {utxo['vout']}")
            print(f"  金额: {utxo['amount']} 聪")
        
        compare_sequence_txid(sender_private_key, recipient_addr, amount_to_send, fee_rate)
        
    except Exception as e:
        logger.error(f"交易创建失败: {e}")
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 