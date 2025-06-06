from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2trAddress, P2wpkhAddress
from bitcoinutils.transactions import TxInput, TxOutput, Transaction, TxWitnessInput

def taproot_to_segwit():
    setup('testnet')

    # 发送方信息
    from_private_key = PrivateKey("cMhdj1dKsv7EftcmLPZtwAvWwFCW8uLLHY136smwCbRBNXouuRxC")

    from_taproot_address = P2trAddress('tb1p484vwajatgstnx82fssqtprljpj9g3ruzj9h8hx03sjnggjcpxesjzzjpg')
    to_segwit_address = P2wpkhAddress('tb1ql67l67sy6zn6d2ztf75chu3h498ydupplwscpt')

    print(f"\n发送方 taproot地址：{from_taproot_address.to_string()}")
    print(f"接收方 segwit地址：{to_segwit_address.to_string()}")

    # 构建交易输入
    txin = TxInput('c305456462278712de24f128effe0b2aee3358d3e89005fdff1035d9755c3f11',
                   0)

    amount_send = 3500
    fee = 300
    total_input = amount_send + fee

    txout = TxOutput(amount_send, to_segwit_address.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    print("\n 未签名的交易：")
    print(tx.serialize())

    input_script = from_taproot_address.to_script_pub_key()
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        [input_script],
        [4000]
    )
    
    tx.witnesses.append(TxWitnessInput([sig]))

    signed_tx = tx.serialize()

    print("\n 已签名的交易:")
    print(signed_tx)

if __name__ == "__main__":
    taproot_to_segwit()