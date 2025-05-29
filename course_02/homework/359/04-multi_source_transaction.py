"""
多来源交易构建

实现一个比特币交易，从三种不同类型的地址（legacy、segwit、taproot）获取UTXO作为输入，
然后将资金支付到一个目标地址，并自动计算手续费，将输入金额减去手续费作为输出金额。

=== 密钥信息 ===
私钥 (HEX): b4f3975a3993bf301a7d0f52f13dd48e992489a97ec4a00495158042bc840b10
私钥 (WIF): cTeSvY5tq6CmPXcrr9puFsxgd3tHH2P5uoW3SYcMLVFBGhY2qExY
公钥 (HEX): 03d3fd1636a4553450e6414b38a86f5f5e2c755d43fce56807f087c7d2f82cfb2d

=== 不同类型的地址 ===
传统地址: msyiGuwFk7vGQcgf5cKDcBcHdJiFrB4xhT
SegWit 地址: tb1q3zcsnruhu7mpl7zcnjcslsw7nuj4s9xavnxhl4
Taproot 地址: tb1p7mwmr705ncwwdgwwpy7ndrm3s6ev44e06e06lfyle9ezmwpn4umq54yqhv


7f42a269b76b1b5d46be1231fb92ae9d6721a43c931d3881c347261cc4223c48
1
147613

c4a56de50622c6d9f3de056888ef93043f133b491e87ab4ea5c94d60440826b9
1
195227

2e816daf794c4d9e37c2ee0f635441cf9dc959cc848d1b813ccb847e86ce8359
0
181039

https://mempool.space/testnet/tx/e8fd4904127fcfc818e5793de6161ff474365b14389836cc3a9fc187b0dfde9e
"""

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress, P2trAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import to_satoshis
import requests


# 广播交易
def broadcast_transaction(signed_tx):
    print("\n手动广播:")
    print("https://mempool.space/testnet/tx/push")
    

# 主函数
def main():
    setup('testnet')

    private_key = PrivateKey('cTeSvY5tq6CmPXcrr9puFsxgd3tHH2P5uoW3SYcMLVFBGhY2qExY')
    public_key = private_key.get_public_key()

    legacy_address = public_key.get_address()
    segwit_address = public_key.get_segwit_address()
    taproot_address = public_key.get_taproot_address()

    legacy_script = legacy_address.to_script_pub_key()
    segwit_script = segwit_address.to_script_pub_key()
    taproot_script = taproot_address.to_script_pub_key()

    # 目标地址
    target_address = P2trAddress('tb1p52hq8twkndu4awmex58xykjv8xj2c467j0r2dvj8y89ndfme09kss2w7ya')

    # utxo
    legacy_txin = TxInput('7f42a269b76b1b5d46be1231fb92ae9d6721a43c931d3881c347261cc4223c48', 1)
    segwit_txin = TxInput('c4a56de50622c6d9f3de056888ef93043f133b491e87ab4ea5c94d60440826b9', 1)
    taproot_txin = TxInput('2e816daf794c4d9e37c2ee0f635441cf9dc959cc848d1b813ccb847e86ce8359', 0)


    # 147613  195227  181039
    utxo_amount1,utxo_amount2,utxo_amount3 = 147613, 195227, 181039
    total_amount = utxo_amount1 + utxo_amount2 + utxo_amount3
    send_amount = 2000
    fee = 400
    # 创建交易输出
    txout = TxOutput(send_amount, target_address.to_script_pub_key())
    self_txout = TxOutput(total_amount - send_amount - fee, taproot_address.to_script_pub_key()) #找零
    
    # 创建聚合交易
    tx = Transaction([legacy_txin, segwit_txin, taproot_txin], [txout, self_txout], has_segwit=True)
    print(f"\n未签名的交易:\n{tx} \n{tx.serialize()}")

    
    # 签名交易
    legacy_sig = private_key.sign_input(
        tx,
        0,
        legacy_script,
    )
    segwit_sig = private_key.sign_segwit_input(
        tx,
        1,
        legacy_script,
        utxo_amount2
    )
    taproot_sig = private_key.sign_taproot_input(
        tx,
        2,
        [legacy_script, segwit_script, taproot_script],
        [utxo_amount1, utxo_amount2, utxo_amount3]
    )

    # script_sig
    legacy_txin.script_sig = Script([legacy_sig, public_key.to_hex()])
    segwit_txin.script_sig = Script([])
    taproot_txin.script_sig = Script([])

    # 隔离见证
    tx.witnesses.append(TxWitnessInput([]))
    tx.witnesses.append(TxWitnessInput([segwit_sig, public_key.to_hex()]))
    tx.witnesses.append(TxWitnessInput([taproot_sig]))

    # 签名交易
    signed_tx = tx.serialize()
    print(f"\n已签名的交易: \n{tx}\n{signed_tx}")

    
    # 广播交易
    broadcast_transaction(signed_tx)


if __name__ == "__main__":
    main()