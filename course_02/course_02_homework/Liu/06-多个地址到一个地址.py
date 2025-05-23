# -*- coding:utf-8 -*-
"""
Author: honey1129
Created time:2025/5/23 21:03
"""
import requests
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import P2trAddress, PrivateKey
from bitcoinutils.script import Script


def main():
    # always remember to setup the network
    setup("testnet")

    priv1 = PrivateKey("cSjpxrYUnud4Z1KsZ3P266szcBQShPXdwojTnsawNy5hFmHRm3BR")
    priv2 = PrivateKey("cNYAUWNshptWrVLb34KyNcLTsF1wUFQbLmPUNnoSYy3iTpuw1znz")
    priv3 = PrivateKey("cW6Apppb5wbMfTyEa8BV4NNUPguxWdaymdQ8nGKhcEqRaWnkcLEt")

    pub1 = priv1.get_public_key()
    pub2 = priv2.get_public_key()
    pub3 = priv3.get_public_key()

    # tb1p5dhpcj0m4ev2zjdra4pre2q2vmv7g07fk5vh7dwl3vkj396hlsjq4cqcuc
    fromAddress1 = pub1.get_taproot_address()

    # tb1qs8r637dl3nvt7qsrfnnl0utau3phaps4gdq84x
    fromAddress2 = pub2.get_segwit_address()

    # mg6utYBmSsybaLSyezY2xGYY6BWgArAGDq
    fromAddress3 = pub3.get_address()

    # UTXO of fromAddress's respectively
    txid1 = "df92dc04fb79a1a62e9df6d0cc6e2758eb5d8bf891f1b4a6552c1c59e6431c0b"
    vout1 = 0
    txid2 = "8c55eef9e4d311eac1d00896fcf16ae9a5a746059fb81a7bfe4ffb0dcfc9b83c"
    vout2 = 0
    txid3 = "133fb738d0660ccc346540f3af7e6cb7d935e8640cd51f08ad838e7201930a4c"
    vout3 = 0

    # all amounts are needed to sign a taproot input
    # (depending on sighash)
    amount1 = to_satoshis(0.000005)
    amount2 = to_satoshis(0.000005)
    amount3 = to_satoshis(0.000005)
    amounts = [amount1, amount2, amount3]


    script_pubkey1 = fromAddress1.to_script_pub_key()
    script_pubkey2 = fromAddress2.to_script_pub_key()
    script_pubkey3 = fromAddress3.to_script_pub_key()
    utxos_script_pubkeys = [script_pubkey1, script_pubkey2, script_pubkey3]


    toAddress = P2trAddress("tb1pmavmahx29wjnclsv0qaudec7lfjgnr2gw3gpwhg4m09v7v3t5hvqga2p0z")

    # create transaction input from tx id of UTXO
    txin1 = TxInput(txid1, vout1)
    txin2 = TxInput(txid2, vout2)
    txin3 = TxInput(txid3, vout3)

    # create transaction output
    txOut = TxOutput(to_satoshis(0.000014), toAddress.to_script_pub_key())

    # create transaction without change output - if at least a single input is
    # segwit we need to set has_segwit=True
    tx = Transaction([txin1, txin2, txin3], [txOut], has_segwit=True)

    sig1 = priv1.sign_taproot_input(tx, 0,utxos_script_pubkeys , amounts)
    sig2 = priv3.sign_segwit_input(tx, 1, script_pubkey2, amount2)
    sig3 = priv3.sign_input(tx, 2, script_pubkey3)

    # set witness sets the witness at a particular input index
    tx.witnesses.append(TxWitnessInput([sig1]))
    tx.witnesses.append(TxWitnessInput([sig2, pub2.to_hex()]))
    tx.witnesses.append(TxWitnessInput([]))
    txin3.script_sig = Script([sig3, pub3.to_hex()])

    print(tx.witnesses)
    signed_tx = tx.serialize()

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + tx.serialize())

    # 广播交易
    print("广播交易...")
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
    main()
