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
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, PrivateKey, P2shAddress
from bitcoinutils.script import Script


def main():
    # always remember to setup the network
    setup("testnet")

    #
    # This script creates a P2SH address containing a P2PK script and sends
    # some funds to it
    #

    # create transaction input from tx id of UTXO (contained 0.1 tBTC)
    txin = TxInput(
        "5eefd8f7e165aba8669540ff64633861b8f9d0bcc748cc2c51dda39b375b5d8f", 0
    )

    # address we are spending from
    from_addr = P2pkhAddress("myYHJtG3cyoRseuTwvViGHgP2efAvZkYa4")

    # secret key of address that we are trying to spent
    sk = PrivateKey("cPeon9fBsW2BxwJTALj3hGzh9vm8C52Uqsce7MzXGS1iFJkPF4AT")
    from_addr2 = sk.get_public_key().get_address()

    print("\nfrom address,P2PK 地址为:", from_addr.to_string())
    print("\nfrom address,P2PK 地址为:", from_addr2.to_string())
    #
    # create transaction output using P2SH scriptPubKey (locking script)
    # (the recipient will give us the final address  but for now we create it
    # for demonstration purposes)
    #

    # secret key corresponding to the pubkey needed for the P2SH (P2PK) transaction
    p2pk_sk = PrivateKey("cRvyLwCPLU88jsyj94L7iJjQX5C2f8koG4G2gevN4BeSGcEvfKe9")
    p2pk_pk = p2pk_sk.get_public_key().to_hex()
   
    # 创建 P2SH 脚本
    redeem_script = Script([p2pk_pk, "OP_CHECKSIG"])

   # 打印 P2SH 地址
    p2sh_addr = P2shAddress.from_script(redeem_script)
    print("to address,P2SH 地址为:", p2sh_addr.to_string())

    txout = TxOutput(to_satoshis(0.00001800), redeem_script.to_p2sh_script_pub_key())

    # no change address - the remaining 0.01 tBTC will go to miners)

    # create transaction from inputs/outputs -- default locktime is used
    tx = Transaction([txin], [txout])

    # print raw transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # use the private key corresponding to the address that contains the
    # UTXO we are trying to spend to create the signature for the txin
    sig = sk.sign_input(tx, 0, from_addr.to_script_pub_key())
    # print(sig)

    # get public key as hex
    pk = sk.get_public_key()
    pk = pk.to_hex()
    # print (pk)

    # set the scriptSig (unlocking script)
    txin.script_sig = Script([sig, pk])
    signed_tx = tx.serialize()

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + signed_tx)
    print("\nTxId:", tx.get_txid())


if __name__ == "__main__":
    main()
