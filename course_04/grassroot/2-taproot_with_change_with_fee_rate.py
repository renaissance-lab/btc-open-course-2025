from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
import requests
from typing import Tuple, List, Dict

def get_utxos(address: str, min_value: int = 600) -> List[Dict]:
    """获取地址的UTXO列表"""
    url = f"https://mempool.space/testnet/api/address/{address}/utxo"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        utxos = response.json()
        
        # 过滤出大于最小值的UTXO
        filtered_utxos = [
            utxo for utxo in utxos
            if utxo.get('value', 0) >= min_value
        ]
        
        if not filtered_utxos:
            raise Exception(f"No UTXOs found with value >= {min_value} satoshis")
            
        # 打印UTXO信息
        print("\nUTXO 信息:")
        print("=" * 50)
        for i, utxo in enumerate(filtered_utxos, 1):
            print(f"UTXO #{i}:")
            print(f"  交易ID: {utxo.get('txid')}")
            print(f"  输出索引: {utxo.get('vout')}")
            print(f"  金额: {utxo.get('value')} 聪 ({utxo.get('value')/100000000:.8f} BTC)")
            print()
            
        return filtered_utxos
        
    except Exception as e:
        logger.error(f"Error fetching UTXOs: {e}")
        raise

def create_taproot_tx(
    sender_private_key: str = "cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT",
    recipient_addr: str = "tb1pezpnfztmzltyvke55cwqc206vdyz8chz4w52yrd8w4ah402jqu2qv9hdkg",
    amount_to_send: float = 0.00001000,
    fee_rate: float = 2.0
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
    
    # 创建输出（包括找零）
    tx_outputs = [
        TxOutput(
            amount_to_send_sats,
            recipient_address.to_script_pub_key()
        )
    ]
    
    # 创建交易
    tx = Transaction(tx_inputs, tx_outputs, has_segwit=True)
    
    # 估算费用,这里很重要，上节课有同学问到
    fee = int(tx.get_vsize() * fee_rate)  
    
    # 计算找零金额
    change_amount = total_input - amount_to_send_sats - fee
    if change_amount <= 0:
        raise Exception("Insufficient funds for transaction and fee")
    
    print("\n金额信息（输出）:")
    print("=" * 50)
    print(f"发送金额: {amount_to_send_sats} 聪 ({amount_to_send:.8f} BTC)")
    print(f"找零金额: {change_amount} 聪 ({change_amount/100000000:.8f} BTC)")
    print(f"手续费: {fee} 聪 ({fee/100000000:.8f} BTC)")
    print(f"总支出: {amount_to_send_sats + change_amount + fee} 聪")
    print()
    
    # 添加找零输出
    tx_outputs.append(
        TxOutput(
            change_amount,
            sender_address.to_script_pub_key()
        )
    )
    
    # 更新交易
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
        "tx_size": tx.get_size(),
        "tx_vsize": tx.get_vsize(),
        "txid": tx.get_txid()
    }
    
    return signed_tx, tx_details

def main():
    try:
        # 创建交易（使用默认参数）
        signed_tx, tx_details = create_taproot_tx()
        
        # 打印交易信息
        print("\n最终交易详情:")
        print("=" * 50)
        print(f"交易ID: {tx_details['txid']}")
        print(f"交易大小: {tx_details['tx_size']} bytes")
        print(f"虚拟大小: {tx_details['tx_vsize']} vbytes")
        print("\n金额详情:")
        print(f"发送金额: {tx_details['amount_sats']} 聪 ({tx_details['amount']:.8f} BTC)")
        print(f"找零金额: {tx_details['change_amount_sats']} 聪 ({tx_details['change_amount']:.8f} BTC)")
        print(f"手续费: {tx_details['fee_sats']} 聪 ({tx_details['fee']:.8f} BTC)")
        print("\n签名后的交易:")
        print(signed_tx)
        print("\n您可以在这里广播交易:")
        print("https://mempool.space/testnet/tx/push")
        
    except Exception as e:
        logger.error(f"交易创建失败: {e}")
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 