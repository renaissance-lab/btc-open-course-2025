# reveal_from_3scripts.py
# 使用 script2（helloaaron 哈希锁）花费之前三脚本生成的 Taproot 地址资金

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import to_satoshis, ControlBlock
import hashlib

def main():
    setup('testnet')

    # Internal Key（Alice）
    alice_priv = PrivateKey("cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT")
    alice_pub = alice_priv.get_public_key()

    # Bob's key（只用于收款）
    bob_priv = PrivateKey("cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG")
    bob_pub = bob_priv.get_public_key()

    # 定义脚本
    hash1 = hashlib.sha256(b"helloworld").hexdigest()
    script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])

    hash2 = hashlib.sha256(b"helloaaron").hexdigest()
    script2 = Script(['OP_SHA256', hash2, 'OP_EQUALVERIFY', 'OP_TRUE'])

    bob_script = Script([bob_pub.to_x_only_hex(), 'OP_CHECKSIG'])

    # 构造 Merkle 树
    tree = [[script1, script2], bob_script]

    # Taproot address
    from_address = alice_pub.get_taproot_address(tree)
    print("🌿 正在花费 Taproot 地址:", from_address.to_string())

    # 替换为你 commit 后的 txid / vout
    txid = "a25375406bbda089c6c64795dc040128ac703dcdd136fd3d85a15bf8efb515da"
    vout = 1
    amount = to_satoshis(0.00001222)  # 来自 commit 阶段

    # 构造输出地址（Bob 收款地址）
    to_addr = bob_pub.get_taproot_address()
    txin = TxInput(txid, vout)
    txout = TxOutput(to_satoshis(0.00001009), to_addr.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    # 构造 Control Block：script2 是在 tree 中索引 1
    cb = ControlBlock(alice_pub, tree, 1, is_odd=from_address.is_odd())

    # Witness 栈 = [preimage, script2, control block]
    tx.witnesses.append(
        TxWitnessInput([
            b"helloaaron".hex(),        # preimage (hex str)
            script2.to_hex(),          # script 本体
            cb.to_hex()                # control block
        ])
    )

    print("\n📤 Reveal 交易 Raw Hex：")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())

if __name__ == '__main__':
    main()