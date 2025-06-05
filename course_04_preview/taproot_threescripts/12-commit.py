# taproot_commit.py
# 构造包含三种脚本的 Taproot 地址，并打印地址与伪造的 commit 交易

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.utils import to_satoshis

import hashlib


def main():
    setup('testnet')

    # Alice 的内部私钥（用于 Taproot 地址）
    alice_priv = PrivateKey("cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT")
    alice_pub = alice_priv.get_public_key()

    # Bob 的私钥，用于后续 P2PK 花费
    bob_priv = PrivateKey("cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG")
    bob_pub = bob_priv.get_public_key()

    # Script 1: 验证 SHA256(preimage) == hash(helloworld)
    hash1 = hashlib.sha256(b"helloworld").hexdigest()
    script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])

    # Script 2: 验证 SHA256(preimage) == hash(helloaaron)
    hash2 = hashlib.sha256(b"helloaaron").hexdigest()
    script2 = Script(['OP_SHA256', hash2, 'OP_EQUALVERIFY', 'OP_TRUE'])

    # Script 3: Bob 的 P2PK 签名脚本
    bob_script = Script([bob_pub.to_x_only_hex(), 'OP_CHECKSIG'])

    # 构建 Merkle Tree
    tree = [[script1, script2], bob_script]

    # 生成 Taproot 地址
    address = alice_pub.get_taproot_address(tree)
    print("🪙 请发送资金至该 Taproot 地址：", address.to_string())


if __name__ == '__main__':
    main()