from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
from typing import Tuple, List, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_replacement_tx(
    original_utxos: List[Dict],
    sender_private_key: str,
    recipient_addr: str,
    amount_to_send: float,
    new_fee_rate: float
) -> Tuple[str, dict]:
    """
    创建RBF替换交易
    
    Args:
        original_utxos: 原始交易使用的UTXO列表
        sender_private_key: 发送方私钥
        recipient_addr: 接收方地址
        amount_to_send: 发送金额（BTC）
        new_fee_rate: 新的费率（sat/vB）
        
    Returns:
        Tuple[str, dict]: (签名后的交易十六进制字符串, 交易详情)
    """
    # 设置测试网
    setup('testnet')
    
    # 发送方信息
    sender_key = PrivateKey(sender_private_key)
    sender_pub = sender_key.get_public_key()
    sender_address = sender_pub.get_taproot_address()
    
    # 接收方地址
    recipient_address = P2trAddress(recipient_addr)
    
    # 计算总输入金额
    total_input = sum(utxo['amount'] for utxo in original_utxos)
    amount_to_send_sats = to_satoshis(amount_to_send)
    
    # 创建输入
    tx_inputs = []
    input_amounts = []
    input_scripts = []
    
    for utxo in original_utxos:
        # RBF交易也需要设置nSequence
        sequence = (0xfffffffe).to_bytes(4, byteorder='little')  # 转换为字节，使用小端序
        tx_input = TxInput(utxo['txid'], utxo['vout'], sequence=sequence)
        tx_inputs.append(tx_input)
        input_amounts.append(utxo['amount'])
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
    
    # 估算新的手续费
    estimated_vsize = initial_tx.get_vsize()
    min_fee_rate = 1.1  # 设置稍高于1 sat/vB的最小费率
    min_fee = int(estimated_vsize * min_fee_rate)
    
    # 确保手续费不低于预计的最小值
    new_fee = max(int(estimated_vsize * new_fee_rate), min_fee)
    
    # 计算新的找零金额
    new_change_amount = total_input - amount_to_send_sats - new_fee
    if new_change_amount <= 0:
        raise Exception(f"资金不足。需要 {amount_to_send_sats + new_fee} 聪，但只有 {total_input} 聪")
    
    # 检查找零是否满足dust限制（一般是330聪）
    if new_change_amount < 330:
        # 如果找零太少，就把它加到手续费中
        new_fee += new_change_amount
        new_change_amount = 0
        logger.info(f"找零金额低于dust限制，将找零 {new_change_amount} 聪添加到手续费中")
    
    # 创建最终输出
    tx_outputs = [
        TxOutput(amount_to_send_sats, recipient_address.to_script_pub_key()),
        TxOutput(new_change_amount, sender_address.to_script_pub_key())
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
        "change_amount": new_change_amount / 100000000,
        "change_amount_sats": new_change_amount,
        "fee": new_fee / 100000000,
        "fee_sats": new_fee,
        "fee_rate": new_fee_rate,
        "tx_size": tx.get_size(),
        "tx_vsize": tx.get_vsize(),
        "txid": tx.get_txid()
    }
    
    return signed_tx, tx_details

def main():
    # 这些参数需要从原始交易中获取
    original_utxos = [
        {
            "txid": "cc2e941ccb355367430b45dcda3daedd9a17ae6b88cc4591323c3ba12acbe8e0",
            "vout": 1,
            "amount": 1115
        },
        {
            "txid": "c4dda5b544f6bcf351071d174dfe23a8325a40e04eceb8f2773837bd9c4a5a48",
            "vout": 0,
            "amount": 3000
        }
    ]
    
    # 交易参数
    sender_private_key = "cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT"
    recipient_addr = "tb1pezpnfztmzltyvke55cwqc206vdyz8chz4w52yrd8w4ah402jqu2qv9hdkg"
    amount_to_send = 0.00001000  # 与原始交易相同
    new_fee_rate = 5.0  # 新的更高费率，5 sat/vB
    
    try:
        # 创建替换交易
        signed_tx, tx_details = create_replacement_tx(
            original_utxos=original_utxos,
            sender_private_key=sender_private_key,
            recipient_addr=recipient_addr,
            amount_to_send=amount_to_send,
            new_fee_rate=new_fee_rate
        )
        
        # 打印交易信息
        print("\nRBF替换交易详情:")
        print("=" * 50)
        print(f"交易ID: {tx_details['txid']}")
        print(f"交易大小: {tx_details['tx_size']} bytes")
        print(f"虚拟大小: {tx_details['tx_vsize']} vbytes")
        print("\n金额详情:")
        print(f"发送金额: {tx_details['amount_sats']} 聪 ({tx_details['amount']:.8f} BTC)")
        print(f"找零金额: {tx_details['change_amount_sats']} 聪 ({tx_details['change_amount']:.8f} BTC)")
        print(f"手续费: {tx_details['fee_sats']} 聪 ({tx_details['fee']:.8f} BTC)")
        print(f"新费率: {tx_details['fee_rate']} sat/vB")
        print("\n签名后的交易:")
        print(signed_tx)
        print("\n请广播这笔替换交易:")
        print("https://mempool.space/testnet/tx/push")
        
    except Exception as e:
        logger.error(f"交易创建失败: {e}")
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 