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
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2trAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import os, sys
import configparser
import requests


conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

def main():
    # always remember to setup the network
    setup("testnet")

    #
    # This script spends from a P2SH address containing a CSV+P2PKH script as
    # created from examples/create_p2sh_csv_p2pkh.py

    # set values
    relative_blocks = 200
    txid = "b2689d2e32e3bb074951be0eeb39afa323905fbee300acda7eab0f20c4b56a4c"
    vout = 0

    seq = Sequence(TYPE_RELATIVE_TIMELOCK, relative_blocks)
    seq_for_n_seq = seq.for_input_sequence()
    assert seq_for_n_seq is not None

    # create transaction input from tx id of UTXO
    txin = TxInput(txid, vout, sequence=seq_for_n_seq)

    # secret key needed to spend P2PKH that is wrapped by P2SH
    p2pkh_sk = PrivateKey(conf.get("testnet3", "private_key_wif"))
    p2pkh_pk = p2pkh_sk.get_public_key().to_hex()
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    # create the redeem script - needed to sign the transaction
    redeem_script = Script(
        [
            seq.for_script(),
            "OP_CHECKSEQUENCEVERIFY",
            "OP_DROP",
            "OP_DUP",
            "OP_HASH160",
            p2pkh_addr.to_hash160(),
            "OP_EQUALVERIFY",
            "OP_CHECKSIG",
        ]
    )

    # send/spend to any random address
    print(conf.get('testnet3', 'tr_hash_multisig_timelock_addr'))
    to_addr = P2trAddress(conf.get('testnet3', 'tr_hash_multisig_timelock_addr'))
    txout = TxOutput(9500, to_addr.to_script_pub_key())

    # create transaction from inputs/outputs
    tx = Transaction([txin], [txout])

    # print raw transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # use the private key corresponding to the address that contains the
    # UTXO we are trying to spend to create the signature for the txin -
    # note that the redeem script is passed to replace the scriptSig
    sig = p2pkh_sk.sign_input(tx, 0, redeem_script)
    # print(sig)

    # set the scriptSig (unlocking script) -- unlock the P2PKH (sig, pk) plus
    # the redeem script, since it is a P2SH
    txin.script_sig = Script([sig, p2pkh_pk, redeem_script.to_hex()])
    signed_tx = tx.serialize()

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + signed_tx)
    print("\nTxId:", tx.get_txid())

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
    main()
