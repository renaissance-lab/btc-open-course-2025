from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import ControlBlock
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

    # Taproot address
    from_address = alice_pub.get_taproot_address(tree)
    print("正在花费Taproot地址：", from_address.to_string())

    txid = "1b3c1409dd8b27db59ffa4e05e135f88c12fad84c39e2d7528d841a9ac8123bf"
    vout = 0
    amount = 600

    to_addr = bob_pub.get_taproot_address()
    print("到Taproot地址：", to_addr.to_string())
    txin = TxInput(txid, vout)
    txout = TxOutput(400, to_addr.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    cb = ControlBlock(alice_pub, tree, 0, is_odd=from_address.is_odd())

    tx.witnesses.append(
        TxWitnessInput([
            b"hellohai".hex(),
            script1.to_hex(),
            cb.to_hex()
        ])
    )

    print("\n交易Raw Hex:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())

if __name__ == "__main__":
    main()