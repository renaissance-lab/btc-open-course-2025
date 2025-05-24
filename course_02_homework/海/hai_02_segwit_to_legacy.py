from bitcoinlib.transactions import Transaction, Input, Output
from bitcoinlib.keys import Key

# 从segwit地址到legacy地址的转账
def segwit_to_legacy_transaction():
    # 发送方信息
    from_private_key = Key("cVgbLBMymtebKVGoriSVWxEBahbGvvx3tuKJftGpaJBcfjujZd4C", network='testnet')

    from_segwit_address = 'tb1ql67l67sy6zn6d2ztf75chu3h498ydupplwscpt'
    to_legacy_address = 'n4juXXS637FKJy9zJsbrCbTLvdQLRZCjST'

    print(f"\n === segwit到legacy地址的转账 ===")

    print(f"\n发送方 SegWit地址：{from_segwit_address}")
    print(f"接收方 Legacy地址：{to_legacy_address}")

    amount_send = 800

    txin = Input(
        prev_txid='7707ef7d842d4805d8698ef25e1998066ac3e8252f12815019aa3933d64f53f1',
        output_n=0,
        network='testnet',
        witness_type='segwit',
        value= 4000
    )

    txout =Output(
        value = amount_send,
        address = to_legacy_address,
        network='testnet'
    )

    tx = Transaction([txin], [txout], network='testnet', witness_type='segwit')


    print("\n 未签名的交易：")
    print(tx.raw_hex())

    tx.sign(from_private_key.private_byte)

    signed_tx = tx.raw_hex()

    print("\n 已签名的交易:")
    print(signed_tx)

if __name__ == '__main__':
    segwit_to_legacy_transaction()