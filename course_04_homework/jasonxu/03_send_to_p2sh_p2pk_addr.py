from bitcoinutils.keys import P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.setup import setup
from bitcoinutils.hdwallet import HDWallet
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK

import os, sys
import configparser
import requests


conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

setup("testnet")

#
# Send from a P2PKH UTXO and send to P2SH, 
# Change back to the same address (not recommended for privacy reasons)
#


from_priv = PrivateKey(conf.get("testnet3", "private_key_wif"))
from_addr = from_priv.get_public_key().get_address()

p2sh_address = P2shAddress(conf.get("testnet3", "p2sh_csv_addr"))
print("To address:", p2sh_address.to_string())

# UTXO's info
txid = "b2689d2e32e3bb074951be0eeb39afa323905fbee300acda7eab0f20c4b56a4c"
vout = 1

txin = TxInput(txid, vout)
txout = TxOutput(9770, p2sh_address.to_script_pub_key())
txout_change = TxOutput(280000, from_addr.to_script_pub_key())
tx = Transaction([txin], [txout, txout_change])
#tx_size = tx.get_size() # looks send to p2sh tx size is wrong
#fee = int(tx_size*1.01)
#print(f"Tx size: {tx_size}, fee: {fee}")
#txout = TxOutput(4468 - fee, p2sh_address.to_script_pub_key())
#tx = Transaction([txin], [txout, txout_change])

sig = from_priv.sign_input(tx, 0, from_addr.to_script_pub_key())

txin.script_sig = Script([sig, from_priv.get_public_key().to_hex()])

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
