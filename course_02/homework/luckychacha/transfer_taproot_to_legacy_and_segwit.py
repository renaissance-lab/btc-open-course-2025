# taproot 到 legacy 和 segwit 地址的转账代码 
# tx hash https://mempool.space/testnet/tx/9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress, P2pkhAddress, P2wpkhAddress

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息（使用正确的私钥）
    from_private_key = PrivateKey('cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh')
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_taproot_address()
    
    # 接收方地址
    # legacy 地址 mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1
    # segwit 地址 tb1qq2x3nt3zzqz7rxgxf03m4tj5eckywehaklggph
    to_address_legacy = P2pkhAddress('mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1')
    to_address_segwit = P2wpkhAddress('tb1qq2x3nt3zzqz7rxgxf03m4tj5eckywehaklggph')

    # to_address = P2trAddress('tb1pqc89pwzzaxlk2vsx9pxpshwzp9ce7rvyxur3esdl3tjwur65f4vstu0svc')
    
    # 创建交易输入
    txin = TxInput(
        '2321dd9157daa490808b5966c1d6c0f7d227084a9ba611ef773886ee5622242e',
        0
    )
    
    # 输入金额（用于签名）
    input_amount = 0.0003
    amounts = [to_satoshis(input_amount)]
    
    # 输入脚本（用于签名）
    input_script = from_address.to_script_pub_key()
    scripts = [input_script]
    
    fee = 0.000004
    # 创建交易输出
    amount_to_send = (input_amount - fee) / 2
    txout_legacy = TxOutput(
        to_satoshis(amount_to_send),
        to_address_legacy.to_script_pub_key()
    )
    txout_segwit = TxOutput(
        to_satoshis(amount_to_send),
        to_address_segwit.to_script_pub_key()
    )
    
    # 创建交易（启用 segwit）
    tx = Transaction([txin], [txout_legacy, txout_segwit], has_segwit=True)
    
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
    print(f"到 Legacy 地址: {to_address_legacy.to_string()}")
    print(f"到 Segwit 地址: {to_address_segwit.to_string()}")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {fee} BTC")
    print(f"发送给 Legacy 地址的金额: {amount_to_send} BTC")
    print(f"发送给 Segwit 地址的金额: {amount_to_send} BTC")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 