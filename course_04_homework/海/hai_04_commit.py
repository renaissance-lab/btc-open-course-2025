from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script

import hashlib

def main():
    setup('testnet')

    # 内部私钥 （用于Taproot地址）
    alice_priv = PrivateKey('cQPNsME8aj6GWQ77RSAcTiWLpEqksEbEfJJtpwG5imwhxEHTqMdc')
    alice_pub = alice_priv.get_public_key()

    # 用于后续P2PK花费
    bob_priv = PrivateKey('cVcCq1VtTRqwze9XD4izFgjug7BsJxH1aRAhDd2keXbsrgBe2Zka')
    bob_pub = bob_priv.get_public_key()
    # Bob的排P2PK签名脚本
    #bob_script = Script([bob_pub.to_x_only_hex(), 'OP_CHECKSIG'])

    # hash(hellohai)
    hash1 = hashlib.sha256(b'hellohai').hexdigest()
    script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])

    # 构造多签脚本 (2-of-3)
    pubkey_A = "02fa38a691fd5b04906cc9fe125d0c5cc71fb0ee56fb99fc2ba5c438ad0a51e6a3"
    pubkey_B = "02174ec79e7a49299712cab443d2a59211c82ffe1656bee8e633434b90b0641b81"
    pubkey_C = "03bf1e677d227500bab16b49b8acc287590f4a33aa0af27b4113fc5a6cd3f40017"
    multi_2_of_3_script = Script([
        'OP_2',
        pubkey_A, pubkey_B, pubkey_C,
        'OP_3',
        'OP_CHECKMULTISIG'
    ])

    timelock = 6*1
    # 时间锁定脚本
    timelock_script = Script([
        'OP_IF',
            timelock,
            'OP_CHECKSEQUENCEVERIFY',
            alice_pub.to_hex(),
            'OP_CHECKSIG',
        'OP_ENDIF'
    ])

    # 构建Merkle树
    tree = [[script1, multi_2_of_3_script], timelock_script]

    # 生成Taproot
    from_address = alice_pub.get_taproot_address(tree)
    print("发送资金到Taproot地址：", from_address.to_string())

if __name__ == '__main__':
    main()