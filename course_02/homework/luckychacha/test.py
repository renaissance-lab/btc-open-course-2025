# Copyright (C) 2018-2025 The python-bitcoin-utils developers
#
# This file is part of python-bitcoin-utils
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoin-utils, including this file, may be copied,
# modified, propagated, or distributed except according to the terms contained
# in the LICENSE file.

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import P2pkhAddress, PrivateKey
from bitcoinutils.script import Script


def main():
    # always remember to setup the network
    setup("testnet")

    # the key that corresponds to the P2WPKH address
    priv1 = PrivateKey("cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh")
    priv2 = PrivateKey("cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh")
    priv3 = PrivateKey("cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh")

    pub1 = priv1.get_public_key()
    pub2 = priv2.get_public_key()
    pub3 = priv3.get_public_key()

    fromAddress1 = pub1.get_address()
    fromAddress2 = pub2.get_segwit_address()
    fromAddress3 = pub3.get_taproot_address()
    print(fromAddress1.to_string())
    print(fromAddress2.to_string())
    print(fromAddress3.to_string())

    # UTXO of fromAddress's respectively
    txid1 = "9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be"
    vout1 = 0
    txid2 = "9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be"
    vout2 = 1
    txid3 = "1a338c80a5be61258ea4e5b5f1ce2d213c22fa340afdd1999a90135e775022bb"
    vout3 = 0

    # all amounts are needed to sign a taproot input
    # (depending on sighash)
    amount1 = to_satoshis(0.00014800)
    amount2 = to_satoshis(0.00014800)
    amount3 = to_satoshis(0.00001)
    amounts = [amount1, amount2, amount3]
    # 计算总输入金额
    total_input = amount1 + amount2 + amount3
    
    # 设置手续费
    fee = to_satoshis(0.000004)  # 0.000004 BTC
    # 计算发送金额
    amount_to_send = total_input - fee

    # all scriptPubKeys are needed to sign a taproot input
    # (depending on sighash) but always of the spend input
    script_pubkey1 = fromAddress1.to_script_pub_key()
    script_pubkey2 = pub2.get_address().to_script_pub_key()
    script_pubkey3 = fromAddress3.to_script_pub_key()
    utxos_script_pubkeys = [script_pubkey1, script_pubkey2, script_pubkey3]

    toAddress = P2pkhAddress('mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1')

    # create transaction input from tx id of UTXO
    txin1 = TxInput(txid1, vout1)
    txin2 = TxInput(txid2, vout2)
    txin3 = TxInput(txid3, vout3)

    # create transaction output
    txOut = TxOutput(amount_to_send, toAddress.to_script_pub_key())

    # create transaction without change output - if at least a single input is
    # segwit we need to set has_segwit=True
    tx = Transaction([txin1, txin2, txin3], [txOut], has_segwit=True)

    print("\nRaw transaction:\n" + tx.serialize())

    print("\ntxid: " + tx.get_txid())
    print("\ntxwid: " + tx.get_wtxid())

    # sign taproot input
    # to create the digest message to sign in taproot we need to
    # pass all the utxos' scriptPubKeys and their amounts

    # 签名所有输入
    # sig1 = from_private_key.sign_input(tx, 0, legacy_script)
    # sig2 = from_private_key.sign_segwit_input(tx, 1, segwit_script, utxos_script_pubkeys[1])
    # sig3 = from_private_key.sign_taproot_input(tx, 2, utxos_script_pubkeys, amounts)


    sig1 = priv1.sign_input(tx, 0, utxos_script_pubkeys[0])
    sig2 = priv2.sign_segwit_input(tx, 1, script_pubkey2, amounts[1])
    sig3 = priv3.sign_taproot_input(tx, 2, utxos_script_pubkeys, amounts)

    #set witness sets the witness at a particular input index
    tx.witnesses = []

    # tx.witnesses.append(TxWitnessInput([sig2, pub2.to_hex()]))
    # tx.witnesses.append(TxWitnessInput([sig3]))
#     tx.set_witness(1, TxWitnessInput([sig2, from_pub.to_hex()]))

    tx.set_witness(1, TxWitnessInput([sig2, pub2.to_hex()]))
    txin1.script_sig = Script([sig1, pub1.to_hex()])
    tx.set_witness(2, TxWitnessInput([sig3]))


    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + tx.serialize())

    print("\nTxId:", tx.get_txid())
    print("\nTxwId:", tx.get_wtxid())

    print("\nSize:", tx.get_size())
    print("\nvSize:", tx.get_vsize())
    # print("\nCore vSize:", 160)


if __name__ == "__main__":
    main()