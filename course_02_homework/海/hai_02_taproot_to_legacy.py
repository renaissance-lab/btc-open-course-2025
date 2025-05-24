from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2trAddress, P2pkhAddress
from bitcoinutils.transactions import TxInput, TxOutput, Transaction, TxWitnessInput
import requests

def taproot_to_legacy():
    setup('testnet')

    # 发送方信息
    from_private_key = PrivateKey("cMhdj1dKsv7EftcmLPZtwAvWwFCW8uLLHY136smwCbRBNXouuRxC")

    from_taproot_address = P2trAddress('tb1p484vwajatgstnx82fssqtprljpj9g3ruzj9h8hx03sjnggjcpxesjzzjpg')
    to_legacy_address = P2pkhAddress('n4juXXS637FKJy9zJsbrCbTLvdQLRZCjST')

    print(f"\n发送方 taproot地址：{from_taproot_address.to_string()}")
    print(f"接收方 legacy地址：{to_legacy_address.to_string()}")

    # 构建交易输入
    txin = TxInput('fe80160ce21787c7c34fb7ae298589391c648896e5717837eedb0e47a0a2874a',
                   1)

    amount_send1 = 1000
    amount_send2 = 3500

    txout1 = TxOutput(amount_send1, to_legacy_address.to_script_pub_key())
    txout2 = TxOutput(amount_send2, from_taproot_address.to_script_pub_key())

    tx = Transaction([txin], [txout1,txout2], has_segwit=True)

    print("\n 未签名的交易：")
    print(tx.serialize())

    input_script = from_taproot_address.to_script_pub_key()
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        [input_script],
        [5000]
    )
    
    tx.witnesses.append(TxWitnessInput([sig]))

    signed_tx = tx.serialize()

    print("\n 已签名的交易:")
    print(signed_tx)

    # 6. 广播交易
    print("\n广播交易...")
    mempool_api = "https://mempool.space/testnet/api/tx"
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
    taproot_to_legacy()