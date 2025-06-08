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

    priv_A = PrivateKey("cQmHDjVN9vyySsterdh5aLMsHP4iWqbg6q2z9KdYxiC7G8VwWMiy")
    priv_B = PrivateKey("cUy4pzV9gQoog9Cfhr4JaMCpqkLaa7YAcg9xwuuEktT3PSkTDp3t")
    priv_C = PrivateKey("cNiGt5Q88aBEzqYd9sVtx8G45bigZ7ScZ6o5aD5zzcaBweHcW2qH")

    # 构造多签脚本 (2-of-3)
    # pubkey_A = "02fa38a691fd5b04906cc9fe125d0c5cc71fb0ee56fb99fc2ba5c438ad0a51e6a3"
    # pubkey_B = "02174ec79e7a49299712cab443d2a59211c82ffe1656bee8e633434b90b0641b81"
    # pubkey_C = "03bf1e677d227500bab16b49b8acc287590f4a33aa0af27b4113fc5a6cd3f40017"

    pubkey_A_hex = priv_A.get_public_key().to_x_only_hex()
    pubkey_B_hex = priv_B.get_public_key().to_x_only_hex()
    pubkey_C_hex = priv_C.get_public_key().to_x_only_hex()

    multi_2_of_3_script = Script([
        "OP_0",
        pubkey_A_hex, 
        "OP_CHECKSIGADD",
        pubkey_B_hex, 
        "OP_CHECKSIGADD",
        pubkey_C_hex,
        "OP_CHECKSIGADD",
        "OP_2", 
        "OP_EQUAL"
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

    txid = "75eee7144b6c90e9c887800e07e2c092d2f640da5c6835b4b16add8dda2e30ab"
    vout = 0
    amount = 700

    to_addr = bob_pub.get_taproot_address()
    print("到Taproot地址：", to_addr.to_string())

    txin = TxInput(txid, vout)
    txout = TxOutput(400, to_addr.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    cb = ControlBlock(alice_pub, tree, 1, is_odd=from_address.is_odd())

    sig_A = priv_A.sign_taproot_input(tx, 0, [from_address.to_script_pub_key()], [amount],
                                      script_path=True,tapleaf_script=multi_2_of_3_script,tweak=False)
    sig_B = priv_B.sign_taproot_input(tx, 0, [from_address.to_script_pub_key()], [amount],
                                      script_path=True,tapleaf_script=multi_2_of_3_script,tweak=False)

    tx.witnesses.append(
        TxWitnessInput([
            sig_B,
            sig_A,
            multi_2_of_3_script.to_hex(),
            cb.to_hex()  
        ])
    )

    print("\n交易Raw Hex:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())

if __name__ == "__main__":
    main()