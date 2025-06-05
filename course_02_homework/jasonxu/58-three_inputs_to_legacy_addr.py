from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import P2trAddress, P2wpkhAddress, P2pkhAddress, PrivateKey
from bitcoinutils.script import Script
import os, sys
import configparser
import requests

conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

def main():
    # always remember to setup the network
    setup("testnet")

    # three addresses are from the same private key
    from_private_key = PrivateKey(conf.get("testnet3", "private_key_wif"))

    legacy_addr = P2pkhAddress(conf.get("testnet3", "legacy_address"))
    segwit_addr = P2wpkhAddress(conf.get("testnet3", "segwit_address"))
    taproot_addr = P2trAddress(conf.get("testnet3", "taproot_address"))
    print(legacy_addr.to_string())
    print(segwit_addr.to_string())
    print(taproot_addr.to_string())

    # UTXO of fromAddress's respectively
    txid1 = "d9f85db96ee9f3bcb728444af4ce3b5b682ac2051cdc44d2f0173023f3453347"
    vout1 = 0
    txid2 = "b99c6efe0686649b02c9e991b37d35004e91594fd19dda797ac502ed20b5021b"
    vout2 = 0
    txid3 = "cb88f7bdc9ec4ab7ce7594fb905bbd413e96ff95c166ecfa05fd2c12c45b54a6"
    vout3 = 1

    # all amounts are needed to sign a taproot input
    # (depending on sighash)
    amount1 = 1800
    amount2 = 3000
    amount3 = 2400
    amounts = [amount1, amount2, amount3]
    fee = 350

    # all scriptPubKeys are needed to sign a taproot input
    # (depending on sighash) but always of the spend input
    script_pubkey1 = legacy_addr.to_script_pub_key()
    script_pubkey2 = segwit_addr.to_script_pub_key()
    script_pubkey3 = taproot_addr.to_script_pub_key()
    utxos_script_pubkeys = [script_pubkey1, script_pubkey2, script_pubkey3]
    segwit_script_pubkey = from_private_key.get_public_key().get_address().to_script_pub_key()
    print("\nsegwit_pub_key:" + script_pubkey2.to_hex())
    print("\nscript_pub_key:" + segwit_script_pubkey.to_hex())

    toAddress = legacy_addr

    # create transaction input from tx id of UTXO
    txin1 = TxInput(txid1, vout1)
    txin2 = TxInput(txid2, vout2)
    txin3 = TxInput(txid3, vout3)

    # create transaction output
    txOut = TxOutput(sum(amounts)-fee, toAddress.to_script_pub_key())

    # create transaction without change output - if at least a single input is
    # segwit we need to set has_segwit=True
    tx = Transaction([txin1, txin2, txin3], [txOut], has_segwit=True)

    print("\nRaw transaction:\n" + tx.serialize())

    print("\ntxid: " + tx.get_txid())
    print("\ntxwid: " + tx.get_wtxid())

    # sign input
    # to create the digest message to sign in taproot we need to
    # pass all the utxos' scriptPubKeys and their amounts
    sig1 = from_private_key.sign_input(tx, 0, utxos_script_pubkeys[0])
    sig2 = from_private_key.sign_segwit_input(tx, 1, segwit_script_pubkey, amounts[1])
    sig3 = from_private_key.sign_taproot_input(tx, 2, utxos_script_pubkeys, amounts)

    #set witness sets the witness at a particular input index
    public_key = from_private_key.get_public_key().to_hex()
    txin1.script_sig = Script([sig1, public_key])
    txin2.script_sig = Script([]) 
    tx.witnesses.append(TxWitnessInput([]))
    tx.witnesses.append(TxWitnessInput([sig2, public_key]))
    tx.witnesses.append(TxWitnessInput([sig3]))
    #tx.set_witness(1, TxWitnessInput([sig2, public_key]))
    #tx.set_witness(2, TxWitnessInput([sig3]))

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + tx.serialize())

    print("\nTxId:", tx.get_txid())
    print("\nTxwId:", tx.get_wtxid())

    print("\nSize:", tx.get_size())
    print("\nvSize:", tx.get_vsize())

    fee = int(tx.get_vsize() *1.05)
    print(f"重新计算手续费: {fee}")
    txOut = TxOutput(sum(amounts)-fee, toAddress.to_script_pub_key())
    tx = Transaction([txin1, txin2, txin3], [txOut], has_segwit=True)   

    sig1 = from_private_key.sign_input(tx, 0, utxos_script_pubkeys[0])
    sig2 = from_private_key.sign_segwit_input(tx, 1, segwit_script_pubkey, amounts[1])
    sig3 = from_private_key.sign_taproot_input(tx, 2, utxos_script_pubkeys, amounts)

    #set witness sets the witness at a particular input index
    tx.witnesses.append(TxWitnessInput([]))
    txin1.script_sig = Script([sig1, public_key])
    tx.witnesses.append(TxWitnessInput([sig2, public_key]))
    txin2.script_sig = Script([]) 
    tx.witnesses.append(TxWitnessInput([sig3]))

    print("\nTxId:", tx.get_txid())
    print("\nTxwId:", tx.get_wtxid())
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    
    signed_tx = tx.serialize()
    print("\nRaw signed transaction:\n" + signed_tx)

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