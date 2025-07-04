from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
from bitcoinutils.script import Script

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息（使用你的私钥）
    from_private_key = PrivateKey('')  # 替换为你的实际私钥
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_taproot_address()
    
    # 接收 Runes 的地址（可以是同一个地址）
    to_address = from_address  # 或者设置为其他 Taproot 地址
    
    # 创建交易输入
    txin = TxInput(
        'd46a0b15f0b4edf99db793d49ca01607f819ec0d5a056bf7fa6c17d9f1b6476e',  # 替换为你的实际 UTXO
        0  # 输出索引
    )
    
    # 输入金额（用于签名）
    input_amount = 0.00001888  # 替换为你的实际输入金额
    amounts = [to_satoshis(input_amount)]
    
    # 输入脚本（用于签名）
    input_script = from_address.to_script_pub_key()
    scripts = [input_script]
    
    # 创建 OP_RETURN 输出（Runestone）
    # 复制你提到的 OP_RETURN 数据: 6a5d07148dde9d011427
    op_return_script = Script([
        'OP_RETURN',
        'OP_13',  # OP_PUSHNUM_13
        '148dde9d011427'  # 直接传 hex 字符串
    ])
    
    # OP_RETURN 输出（0 金额）
    op_return_output = TxOutput(0, op_return_script)
    
    # 接收 Runes 的输出（最小 546 sats）
    runes_amount = 0.00000546  # 546 sats
    runes_output = TxOutput(
        to_satoshis(runes_amount),
        to_address.to_script_pub_key()
    )
    
    # 找零输出（如果需要）
    fee = 0.00000300  # 手续费
    change_amount = input_amount - runes_amount - fee
    
    outputs = [op_return_output, runes_output]
    
    # 如果有找零，添加找零输出
    if change_amount > 0.00000546:  # 大于 dust limit
        change_output = TxOutput(
            to_satoshis(change_amount),
            from_address.to_script_pub_key()
        )
        outputs.append(change_output)
    
    # 创建交易（启用 segwit）
    tx = Transaction([txin], outputs, has_segwit=True)
    
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
    print(f"到地址 (P2TR): {to_address.to_string()}")
    print(f"Runes 接收金额: {runes_amount} BTC (546 sats)")
    print(f"手续费: {fee} BTC")
    print(f"找零: {change_amount} BTC" if change_amount > 0.00000546 else "无找零")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    
    print("\n OP_RETURN 数据:")
    print(f"Runestone: 148dde9d011427")
    print(f"目标 Rune: I•NEED•TEST•RUNES")
    
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main()