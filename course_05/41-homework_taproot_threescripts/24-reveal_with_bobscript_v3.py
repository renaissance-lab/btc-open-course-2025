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

    # Bob's key（用于解锁）
    bob_priv = PrivateKey("cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG")
    bob_pub = bob_priv.get_public_key()

    # 定义脚本
    hash1 = hashlib.sha256(b"helloworld").hexdigest()
    script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])
    hash2 = hashlib.sha256(b"helloaaron").hexdigest()
    script2 = Script(['OP_SHA256', hash2, 'OP_EQUALVERIFY', 'OP_TRUE'])
    bob_script = Script([bob_pub.to_x_only_hex(), 'OP_CHECKSIG'])

    # 构造 Merkle 树
    tree = [[script1, bob_script],script2]


    # Taproot address
    from_address = alice_pub.get_taproot_address(tree)
    print("🌿 正在花费 Taproot 地址:", from_address.to_string())

    # 调试信息：打印 tree 结构和每个 leaf 的 to_hex
    print('\n[调试] Merkle tree 结构:')
    for idx, leaf in enumerate(tree):
        if isinstance(leaf, list):
            for subidx, subleaf in enumerate(leaf):
                print(f'  leaf {idx}-{subidx}:', subleaf.to_hex())
        else:
            print(f'  leaf {idx}:', leaf.to_hex())
    print('[调试] bob_script hex:', bob_script.to_hex())
    print('[调试] from_address:', from_address.to_string())
    print('tree结构:', tree)
    print('bob_script hex:', bob_script.to_hex())
    print('from_address:', from_address.to_string())
    print('from_address scriptPubKey:', from_address.to_script_pub_key().to_hex())
    print('alice_pub hex:', alice_pub.to_hex())
    print('bob_pub hex:', bob_pub.to_hex())

    # tweaked_pubkey = from_address.to_script_pub_key().to_hex()
    # print('[调试] alice_pub.get_taproot_pubkey(tree):', tweaked_pubkey.hex())
    # if hasattr(from_address, 'xonly_pubkey'):
    #     print('[调试] from_address.xonly_pubkey:', from_address.xonly_pubkey.hex())
    # elif hasattr(from_address, 'pubkey'):
    #     print('[调试] from_address.pubkey:', tweaked_pubkey.hex())

    spk_hex = from_address.to_script_pub_key().to_hex()
    tweaked_pubkey_hex = spk_hex[2:]  # 跳过前2位（OP_1=0x51=1字节=2 hex位）
    print('链上x-only公钥:', tweaked_pubkey_hex)

    # 替换为你 commit 后的 txid / vout
    txid = "4475ddf37e82053c40710bd47c22c392b5faad3d89a19801e13a15b9741d6434"
    vout = 1
    amount = to_satoshis(0.00001666)  # 来自 commit 阶段

    # 构造输出地址（Bob 收款地址）
    to_addr = bob_pub.get_taproot_address()
    txin = TxInput(txid, vout)
    txout = TxOutput(to_satoshis(0.00001400), to_addr.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    # 用 Bob 的私钥对 bob_script 做 script path spend
    sig = bob_priv.sign_taproot_input(
        tx,
        0,
        [from_address.to_script_pub_key()],
        [amount],
        script_path=True,
        tapleaf_script=bob_script,
        tweak=False
    )
    cb = ControlBlock(alice_pub, tree, 1, is_odd=from_address.is_odd())
    # print('[调试] cb.get_tweaked_pubkey:', cb.get_tweaked_pubkey().to_hex())
    # assert cb.get_tweaked_pubkey() == from_address.get_pubkey(), 'Control block tweaked pubkey 与 from_address 不一致！'
    tx.witnesses.append(TxWitnessInput([sig, bob_script.to_hex(), cb.to_hex()]))

    print("\n📤 Bob script 解锁（script path spend）Raw Hex：")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())

if __name__ == '__main__':
    main()