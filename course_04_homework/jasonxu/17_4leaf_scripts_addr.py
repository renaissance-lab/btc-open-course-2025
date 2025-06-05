# 构造包含三种脚本的 Taproot 地址，

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Sequence
from bitcoinutils.utils import to_satoshis

import hashlib
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK

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

    # 生成 Taproot 地址
    address = alice_pub.get_taproot_address(tree)
    print("🪙 请发送资金至该 Taproot 地址：", address.to_string())
    conf.set('testnet3', 'tr_4leaf_scripts_addr', address.to_string())
    conf.write(open(conf_file, "w"))

if __name__ == '__main__':
    main()