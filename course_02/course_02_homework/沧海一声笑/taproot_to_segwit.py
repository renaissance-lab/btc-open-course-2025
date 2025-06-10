"""
从 Taproot 地址转账到 SegWit 地址
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress, P2wpkhAddress

def main():
    # 设置测试网
    setup('regtest')
    
    # 发送方信息
    from_private_key = PrivateKey('cRN6iYkJookUYiBH32PWyaf1arRDGq6gDbw7QRi3R5b2nPJdnkuv')
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_taproot_address()
    
    # 接收方地址 (SegWit)
    to_address = P2wpkhAddress('bcrt1qj5q6huak207m39d4g3x33asyywdph4ytqlawvn')
    
    # 创建交易输入
    txin = TxInput(
        'd9b9dd2f4153c5aa8ceba90845d6681fa48c9e8c2212470311d116df7e4225fb',
        0
    )
    
    # 输入金额（用于签名）
    input_amount = 0.78125000
    amounts = [to_satoshis(input_amount)]
    
    # 输入脚本（用于签名）
    input_script = from_address.to_script_pub_key()
    scripts = [input_script]
    
    # 创建交易输出
    amount_to_send = 0.4
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )
    
    # 创建找零输出（返回到发送方地址）
    change_amount = input_amount - amount_to_send - 0.00001  # 减去1000聪手续费
    change_txout = TxOutput(
        to_satoshis(change_amount),
        from_address.to_script_pub_key()
    )
    
    # 创建交易（启用 segwit）
    tx = Transaction([txin], [txout, change_txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())
    
    # 签名交易
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        scripts,
        amounts
    )
    
    # 添加见证数据
    tx.witnesses.append(TxWitnessInput([sig]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从地址 (P2TR): {from_address.to_string()}")
    print(f"到地址 (SegWit): {to_address.to_string()}")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"找零金额: {change_amount} BTC")
    print(f"手续费: 0.00001 BTC (1000 聪)")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 