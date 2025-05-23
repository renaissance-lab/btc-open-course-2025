import requests
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress


def main():
    # 设置测试网
    setup('testnet')

    # 发送方信息（使用正确的私钥）
    from_private_key = PrivateKey('cSjpxrYUnud4Z1KsZ3P266szcBQShPXdwojTnsawNy5hFmHRm3BR')
    from_pub = from_private_key.get_public_key()
    # 发送方地址
    from_address = from_pub.get_taproot_address()

    # 接收方地址
    to_address = P2pkhAddress('mkDeKvM5BwXHt4SDLxE5kjwDiNtc8UUzmC')

    # 创建交易输入
    txin = TxInput(
        'b6f38a041ee4fbc0e323e8bfc79f57dd44ebd14f40699345240e25120ee232d4',
        1
    )

    # 输入金额（用于签名）
    input_amount = 0.005
    amounts = [to_satoshis(input_amount)]


    # 创建交易输出
    amount_to_send = 0.00049
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )

    # 创建交易（启用 segwit）
    tx = Transaction([txin], [txout], has_segwit=True)

    print("\n未签名的交易:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())

    # 签名交易
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        [from_address.to_script_pub_key()],
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
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {input_amount - amount_to_send} BTC")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

    # 广播交易
    print("\n广播交易...")
    mempool_api = "https://mempool.space/testnet4/api/tx"
    try:
        response = requests.post(mempool_api, data=signed_tx)
        if response.status_code == 200:
            txid = response.text
            print(f"交易成功！")
            print(f"交易ID: {txid}")
            print(f"查看交易: https://mempool.space/testnet/tx/{txid}")
        else:
            print(f"广播失败: {response.text}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
