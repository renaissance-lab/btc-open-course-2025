# 使用 script1（hellojason 哈希锁）花费之前三脚本生成的 Taproot 地址资金

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput, Sequence
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import hashlib
import os, sys
import configparser
import requests


conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

def main():
    setup('testnet')

   # Alice 的内部私钥（用于 Taproot 地址）
    alice_priv = PrivateKey(conf.get("testnet3", "private_key_wif"))
    alice_pub = alice_priv.get_public_key()
    print(f"alice's pubkey:{alice_pub.to_hex()}, len:{len(alice_pub.to_hex())}")

    # Bob 的私钥，用于multisig script path & CSV timelock script path 
    bob_priv = PrivateKey(conf.get("testnet3_source", "private_key_wif"))
    bob_pub = bob_priv.get_public_key()    
    print(f"bob's pubkey:{bob_pub.to_hex()}, len:{len(bob_pub.to_hex())}")

    # 重建脚本树
     # Script 1: 验证 SHA256(preimage) == hash(hellojason)
    hash1 = hashlib.sha256(b"hellojason").hexdigest()
    script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])
    print(f"1st script str:{script1.to_hex()}")

    # Script 2: 2-of-2 multisig
    script2 = Script(
        ["OP_0",
         alice_pub.to_x_only_hex(),
         "OP_CHECKSIGADD",
         bob_pub.to_x_only_hex(),
         "OP_CHECKSIGADD",
         "OP_2", 
         "OP_EQUAL"
        ]
    )
    print(f"2nd script str:{script2.to_hex()}")

    # Script 3: CSV timelock
    relative_blocks = 200 # 200 blocks on testnet3, 需要几十分钟解锁
    seq = Sequence(TYPE_RELATIVE_TIMELOCK, relative_blocks)
    # create the redeem script
    script3 = Script(
        [
            seq.for_script(),
            "OP_CHECKSEQUENCEVERIFY",
            "OP_DROP",
            bob_pub.to_x_only_hex(),
            "OP_CHECKSIG"
        ]
    )
    print(f"3rd script str:{script3.to_hex()}")    

     # Script 4: bob's siglock
    script4 = Script(
        [
            bob_pub.to_x_only_hex(),
            "OP_CHECKSIG"
        ]
    )
    print(f"4th script str:{script4.to_hex()}")        

    # 构建 Merkle Tree
    tree = [[script1, script2], [script3, script4]]
   
    taproot_address = alice_pub.get_taproot_address(tree)

    # 输入信息
    commit_txid = "6ee915fd19cfbcfd2c05024decad4cc540504fbbb1bc64bd6e05b63d6c1d9ca2" 
    vout = 1
    input_amount = 8730  
    output_amount = 800
    fee = 230

   # 构建交易
    txin = TxInput(commit_txid, vout)
    # 输出到 Alice 的简单 Taproot 地址
    txout = TxOutput(output_amount, alice_pub.get_taproot_address().to_script_pub_key())
    txout_change = TxOutput(input_amount-output_amount-fee, taproot_address.to_script_pub_key())
    tx = Transaction([txin], [txout, txout_change], has_segwit=True)

    cb = ControlBlock(alice_pub, tree, 3, is_odd=taproot_address.is_odd())

    sigB = bob_priv.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],
        [input_amount],
        script_path=True,
        tapleaf_script=script4,
        tweak=False,
    )

    tx.witnesses.append(
        TxWitnessInput([
            sigB,         # (hex str)
            script4.to_hex(),          # script 本体
            cb.to_hex()                # control block
        ])
    )

    print(f"TxId: {tx.get_txid()}")
    #print("\nTxwId:", tx.get_wtxid())
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")

    signed_tx = tx.serialize()
    print(f"Raw Tx: {signed_tx}")

     # 广播交易
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

if __name__ == '__main__':
    main()