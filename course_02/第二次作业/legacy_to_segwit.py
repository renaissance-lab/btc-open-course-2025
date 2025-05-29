"""
SegWit到Legacy地址的比特币交易
本文件实现从SegWit地址向Legacy地址发送比特币的交易。
"""

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput

def main():
    # 设置测试网
    setup('testnet')

    # 发送方信息（SegWit地址）
    from_private_key = PrivateKey('cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6')
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_segwit_address()

    # 获取脚本代码
    script_code = from_pub.get_segwit_address().to_script_pub_key()

    # 接收方信息（Legacy地址）
    to_address = P2pkhAddress('mgMzeGduaTgTAywnq9BND2Ard4iSPLxqoW')

    print(f"\n发送方 SegWit 地址: {from_address.to_string()}")
    print(f"接收方 Legacy 地址: {to_address.to_string()}")

    # 创建交易输入
    txin = TxInput(
        'a5fd7178ffd24d03d043da255b96a5f31703ebaff3ef93fcb54f189c48f762a1',
        1  # vout
    )

    # 计算金额（单位：sats）
    total_input = 1200
    fee = 200
    amount_to_send = total_input - fee

    # 创建交易输出
    txout = TxOutput(amount_to_send, to_address.to_script_pub_key())

    # 创建交易
    tx = Transaction([txin], [txout], has_segwit=True)  # SegWit 交易必须设置 has_segwit=True

    print("\n未签名的交易:")
    print(tx.serialize())

    # 签名交易
    sig = from_private_key.sign_segwit_input(
        tx,
        0,
        script_code,  # 使用从公钥派生的脚本代码
        total_input  # SegWit 交易必须提供输入金额
    )

    # 获取公钥
    public_key = from_private_key.get_public_key().to_hex()

    # 设置赎回脚本
    txin.script_sig = Script([])  # SegWit 交易的 script_sig 必须为空

    # 设置见证数据
    tx.witnesses.append(TxWitnessInput([sig, public_key]))  # 使用 TxWitnessInput 包装见证数据

    # 获取签名后的交易
    signed_tx = tx.serialize()

    print("\n已签名的交易:")
    print(signed_tx)

    print("\n交易信息:")
    print(f"从地址: {from_address.to_string()} (SegWit)")
    print(f"到地址: {to_address.to_string()} (Legacy)")
    print(f"发送金额: {amount_to_send} sats")
    print(f"手续费: {fee} sats")
    print("\n手动广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main()