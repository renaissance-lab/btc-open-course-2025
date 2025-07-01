from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
from typing import Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Taproot输出的dust限制（聪）
DUST_LIMIT = 330

def create_acceleration_tx(
    parent_txid: str,
    parent_vout: int,
    parent_amount_sats: int,
    sender_private_key: str,
    recipient_addr: str,
    fee_rate: float
) -> Tuple[str, dict]:
    """
    创建加速交易
    
    Args:
        parent_txid: 父交易ID（需要加速的交易）
        parent_vout: 父交易输出索引（找零输出）
        parent_amount_sats: 父交易输出金额（找零金额，单位：聪）
        sender_private_key: 发送方私钥
        recipient_addr: 接收方地址
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
    
    # 接收方地址
    recipient_address = P2trAddress(recipient_addr)
    
    # 创建输入
    tx_input = TxInput(parent_txid, parent_vout)
    
    # 创建一个初始交易来估算大小
    initial_tx = Transaction(
        [tx_input],
        [TxOutput(0, recipient_address.to_script_pub_key())],
        has_segwit=True
    )
    
    # 估算手续费
    fee = int(initial_tx.get_vsize() * fee_rate)
    
    # 计算实际可发送金额
    amount_to_send = parent_amount_sats - fee
    
    # 检查输出是否小于dust限制
    if amount_to_send < DUST_LIMIT:
        raise Exception(f"Output would be dust: {amount_to_send} sats < {DUST_LIMIT} sats")
    
    # 检查输入金额是否足够
    if amount_to_send <= 0:
        raise Exception("Fee would exceed input amount")
    
    # 创建最终输出
    tx_output = TxOutput(
        amount_to_send,
        recipient_address.to_script_pub_key()
    )
    
    # 创建交易
    tx = Transaction([tx_input], [tx_output], has_segwit=True)
    
    # 签名交易
    sig = sender_key.sign_taproot_input(
        tx,
        0,
        [sender_address.to_script_pub_key()],
        [parent_amount_sats]
    )
    tx.witnesses.append(TxWitnessInput([sig]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    # 准备交易详情
    tx_details = {
        "parent_txid": parent_txid,
        "from_address": sender_address.to_string(),
        "to_address": recipient_addr,
        "input_amount": parent_amount_sats,
        "output_amount": amount_to_send,
        "fee": fee,
        "fee_rate": fee_rate,
        "tx_size": tx.get_size(),
        "tx_vsize": tx.get_vsize(),
        "txid": tx.get_txid()
    }
    
    return signed_tx, tx_details

def main():
    # 这些参数需要根据之前低费率交易的结果来填写
    parent_txid = "在这里填入低费率交易的交易ID"
    parent_vout = 1  # 通常找零输出的索引是1
    parent_amount_sats = 0  # 在这里填入低费率交易的找零金额（聪）
    
    # 交易参数
    sender_private_key = "cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT"
    recipient_addr = "tb1pezpnfztmzltyvke55cwqc206vdyz8chz4w52yrd8w4ah402jqu2qv9hdkg"
    fee_rate = 10.0  # 高费率，10 sat/vB，帮助加速确认
    
    try:
        # 创建加速交易
        signed_tx, tx_details = create_acceleration_tx(
            parent_txid=parent_txid,
            parent_vout=parent_vout,
            parent_amount_sats=parent_amount_sats,
            sender_private_key=sender_private_key,
            recipient_addr=recipient_addr,
            fee_rate=fee_rate
        )
        
        # 打印交易信息
        print("\n加速交易详情:")
        print("=" * 50)
        print(f"父交易ID: {tx_details['parent_txid']}")
        print(f"交易ID: {tx_details['txid']}")
        print(f"交易大小: {tx_details['tx_size']} bytes")
        print(f"虚拟大小: {tx_details['tx_vsize']} vbytes")
        print("\n金额详情:")
        print(f"输入金额: {tx_details['input_amount']} 聪 ({tx_details['input_amount']/100000000:.8f} BTC)")
        print(f"输出金额: {tx_details['output_amount']} 聪 ({tx_details['output_amount']/100000000:.8f} BTC)")
        print(f"手续费: {tx_details['fee']} 聪 ({tx_details['fee']/100000000:.8f} BTC)")
        print(f"费率: {tx_details['fee_rate']} sat/vB")
        print(f"\n注意: 输出金额必须大于 {DUST_LIMIT} 聪")
        print("\n签名后的交易:")
        print(signed_tx)
        print("\n请在父交易已经在mempool中后，再广播这笔加速交易:")
        print("https://mempool.space/testnet/tx/push")
        
    except Exception as e:
        logger.error(f"交易创建失败: {e}")
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 