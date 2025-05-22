# 多种输入类型（legacy、segwit、taproot）到legacy地址的转账代码
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.script import Script

def main():
    # 设置测试网
    setup('testnet')
    
    # 私钥
    from_private_key = PrivateKey('cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh')
    from_pub = from_private_key.get_public_key()
    
    # 从同一私钥生成3种不同类型的地址
    legacy_address = from_pub.get_address()
    segwit_address = from_pub.get_segwit_address()
    taproot_address = from_pub.get_taproot_address()
    
    # 接收方地址（Legacy）
    to_address = P2pkhAddress('mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1')
    
    # 显示各种地址信息
    print("\n=== 地址信息 ===")
    print(f"私钥 WIF: {from_private_key.to_wif()}")
    print(f"Legacy 地址: {legacy_address.to_string()}")
    print(f"SegWit 地址: {segwit_address.to_string()}")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"目标 Legacy 地址: {to_address.to_string()}")
    
    # 创建多个交易输入 - 请替换为您实际的UTXO信息
    # 创建Legacy输入
    txin_legacy = TxInput(
        '9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be',  # 请替换为实际的交易ID
        0  # 请替换为实际的输出索引
    )
    
    # 创建SegWit输入
    txin_segwit = TxInput(
        '9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be',  # 请替换为实际的交易ID
        1  # 请替换为实际的输出索引
    )
    
    # 创建Taproot输入
    txin_taproot = TxInput(
        '7117d354e2ef021c6a8a2b668c09645015c857ea2f2cc7e3a5f77a4c98bff312',  # 请替换为实际的交易ID
        2  # 请替换为实际的输出索引
    )
    
    # Legacy 地址: mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1
    # SegWit 地址: tb1qq2x3nt3zzqz7rxgxf03m4tj5eckywehaklggph
    # Taproot 地址: tb1p9q80mtqns48e8dm4gkuq0n5tx9zdwqqqh9skyagqrtq3q7jvdqfqe02xas
    legacy_amount = 0.00014800
    segwit_amount = 0.00014800
    taproot_amount = 0.00010000
    
    # 计算总输入金额
    total_input = legacy_amount + segwit_amount + taproot_amount
    
    # 设置手续费
    fee = 0.000004
    
    # 计算发送金额
    amount_to_send = total_input - fee
    
    # 创建交易输出
    txout = TxOutput(to_satoshis(amount_to_send), to_address.to_script_pub_key())
    
    # 创建交易（由于包含SegWit和Taproot输入，设置has_segwit=True）
    tx = Transaction([txin_legacy, txin_segwit, txin_taproot], [txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 为Legacy输入签名
    legacy_script = legacy_address.to_script_pub_key()
    sig_legacy = from_private_key.sign_input(
        tx,
        0,  # 第一个输入的索引
        legacy_script
    )
    txin_legacy.script_sig = Script([sig_legacy, from_pub.to_hex()])
    
    # 为SegWit输入签名
    # 获取P2PKH等效脚本（SegWit要求）
    sig_segwit = from_private_key.sign_segwit_input(
        tx,
        1,  # 第二个输入的索引
        from_pub.get_address().to_script_pub_key(),
        to_satoshis(segwit_amount)
    )
    txin_segwit.script_sig = Script([])  # SegWit的scriptSig为空
    # 添加SegWit见证数据
    tx.witnesses.append(TxWitnessInput([sig_segwit, from_pub.to_hex()]))
    
    # 为Taproot输入签名
    taproot_script = taproot_address.to_script_pub_key()
    sig_taproot = from_private_key.sign_taproot_input(
        tx,
        2,  # 第三个输入的索引
        [taproot_script],
        [to_satoshis(taproot_amount)]
    )
    # 添加Taproot见证数据
    tx.witnesses.append(TxWitnessInput([sig_taproot]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从 Legacy 地址: {legacy_address.to_string()}")
    print(f"从 SegWit 地址: {segwit_address.to_string()}")
    print(f"从 Taproot 地址: {taproot_address.to_string()}")
    print(f"到 Legacy 地址: {to_address.to_string()}")
    print(f"总输入金额: {total_input} BTC")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {fee} BTC")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main()