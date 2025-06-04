"""
创建一个带有三解锁脚本的Taproot地址，并使用四个路径来解锁花费
花费方式：
1. Script Path 1：任何人提供preimage "helloworld" 来花费
2. Script Path 2：Bob&Alice&Charlie 2-of-3多签花费
3. Script Path 3：时间锁+Alice，当超过4600000个区块后，Alice可直接使用私钥解锁
4. Key Path：内部私钥直接花费
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput,TxWitnessInput
from bitcoinutils.keys import PrivateKey
from bitcoinutils.constants import  SIGHASH_ALL
from bitcoinutils.utils import ControlBlock
import hashlib
# 直接使用 Script 类中的操作码常量
OP_0 = Script.OP_0
OP_2 = Script.OP_2
OP_3 = Script.OP_3
OP_CHECKMULTISIG = Script.OP_CHECKMULTISIG
OP_CHECKSIG = Script.OP_CHECKSIG
OP_SHA256 = Script.OP_SHA256
OP_EQUALVERIFY = Script.OP_EQUALVERIFY
OP_TRUE = Script.OP_TRUE
OP_CHECKLOCKTIMEVERIFY = Script.OP_CHECKLOCKTIMEVERIFY
OP_DROP = Script.OP_DROP

def main():
    # 设置测试网
    setup('testnet')

    # 内部密钥（内部密钥，Key Path）
    key_private = PrivateKey('')
    key_public = key_private.get_public_key()

    # Alice 的密钥（Script Path 2，2-of-3多签）
    alice_private = PrivateKey('')
    alice_public = alice_private.get_public_key()

    # Bob 的密钥（Script Path 2，2-of-3多签）
    bob_private = PrivateKey('')
    bob_public = bob_private.get_public_key()

    # Charlie 的密钥（Script Path 2，2-of-3多签）
    charlie_private = PrivateKey('')
    charlie_public = charlie_private.get_public_key()

    # 创建 preimage 的哈希（Script Path 1）
    preimage = "helloworld"
    preimage_bytes = preimage.encode('utf-8')
    preimage_hash = hashlib.sha256(preimage_bytes).hexdigest()

    # Script Path 1: 哈希锁脚本 - 验证 preimage
    hash_script = Script([
        'OP_SHA256',
        preimage_hash,
        'OP_EQUALVERIFY',
        'OP_TRUE'
    ])

    # Script Path 2: bob&alice&charlie 的多签脚本 - P2PK
    bob_alice_charlie_script = Script([
        OP_2,
        bob_public.to_x_only_hex(),
        alice_public.to_x_only_hex(),
        charlie_public.to_x_only_hex(),
        OP_3,
        OP_CHECKMULTISIG
    ])
    # Script Path 3: 当超过4600000个区块后Alice可直接使用私钥签名来花费
    time_over_alice_script = Script([
        4600000,
        OP_CHECKLOCKTIMEVERIFY,
        OP_DROP,
        alice_public.to_x_only_hex(),
        OP_CHECKSIG
    ])

    # 按照验证的三脚本模式创建脚本树：平铺结构
    all_leafs = [[hash_script, bob_alice_charlie_script], time_over_alice_script]
    three_path_taproot_address = key_public.get_taproot_address(all_leafs)
    # 这里需要查一下
    control_block = ControlBlock(key_public, [[all_leafs]], 0, is_odd=three_path_taproot_address.is_odd())
    # 输出三脚本地址
    print(f"\nTaproot 地址: {three_path_taproot_address.to_string()}")

    print(f"\n=== === === === ===  多路径解锁 === === === === ===  ")
    print(f"\n=== === === === ===  path1 提供preimage解锁 === === === === ===  ")
    # Commit 信息
    commit_txid1 = "4fd83128fb2df7cd25d96fdb6ed9bea26de755f212e37c3aa017641d3d2d2c6d"
    input_amount = 0.00001200  # 1200 satoshis
    output_amount = 0.00001000  # 1000 satoshi
    txin = TxInput(commit_txid1, 0)
    txout = TxOutput(to_satoshis(output_amount), alice_public.get_taproot_address().to_script_pub_key())  # 发送给Alice
    tx = Transaction([txin], [txout], has_segwit=True)
    tx.witnesses.append(TxWitnessInput([preimage_bytes.hex(), all_leafs.to_hex(), control_block.to_hex()]))
    print(f"Path1 交易哈希: {tx.get_txid()}")
    print(f"\n=== === === === ===  path2 提供Bob&Alice&Charlie 2-of-3多签解锁 === === === === ===  ")
    commit_txid2 = "4fd83128fb2df7cd25d96fdb6ed9bea26de755f212e37c3aa017641d3d2d2c6d"
    txin = TxInput(commit_txid2, 0)
    txout = TxOutput(to_satoshis(output_amount), alice_public.get_address())
    tx = Transaction([txin], [txout], has_segwit=True)

    # 生成两个签名 (Bob和Alice)
    sig_bob = bob_private.sign_taproot_input(
        tx, 0, [three_path_taproot_address.to_script_pub_key()],
        [to_satoshis(input_amount)], script_path=True,
        tapleaf_script=three_path_taproot_address
    )

    sig_alice = alice_private.sign_taproot_input(
        tx, 0, [three_path_taproot_address.to_script_pub_key()],
        [to_satoshis(input_amount)], script_path=True,
        tapleaf_script=three_path_taproot_address
    )

    # 构建见证数据 (注意: CHECKMULTISIG需要额外一个OP_0)
    tx.witnesses.append(TxWitnessInput([
        'OP_0',  # CHECKMULTISIG的额外元素
        sig_bob.to_hex(),
        sig_alice.to_hex(),
        three_path_taproot_address.to_hex(),
        key_public.get_taproot_control_block(three_path_taproot_address, all_leafs).to_hex()
    ]))

    print(f"Path2 交易哈希: {tx.get_txid()}")

    print(f"\n=== === === === ===  path3 时间锁+Alice私钥解锁 === === === === ===  ")
    commit_txid3 = "4fd83128fb2df7cd25d96fdb6ed9bea26de755f212e37c3aa017641d3d2d2c6d"
    txin = TxInput(commit_txid3, 0)
    txout = TxOutput(to_satoshis(output_amount), alice_public.get_address())
    tx = Transaction([txin], [txout], has_segwit=True)

    # 设置锁定时间 (必须大于等于脚本中的80000)
    tx.locktime = 80000

    # Alice签名
    sig_alice = alice_private.sign_taproot_input(
        tx, 0, [three_path_taproot_address.to_script_pub_key()],
        [to_satoshis(input_amount)], script_path=True,
        tapleaf_script=all_leafs
    )

    tx.witnesses.append(TxWitnessInput([
        sig_alice.to_hex(),
        all_leafs.to_hex(),
        key_public.get_taproot_control_block(three_path_taproot_address, all_leafs).to_hex()
    ]))

    print(f"Path3 交易哈希: {tx.get_txid()}")

    print(f"\n=== === === === ===  path4 内部私钥直接解锁 === === === === ===  ")

    commit_txid4 = "4fd83128fb2df7cd25d96fdb6ed9bea26de755f212e37c3aa017641d3d2d2c6d"
    txin = TxInput(commit_txid4, 0)
    receiving_address_pubkey = alice_public.get_taproot_address().to_script_pub_key()
    txout = TxOutput(to_satoshis(output_amount), receiving_address_pubkey)
    tx = Transaction([txin], [txout], has_segwit=True)
    sig = key_private.sign_taproot_input(
        tx,
        0,
        [three_path_taproot_address.to_script_pub_key()],
        [to_satoshis(input_amount)],
        script_path=False,
        tapleaf_scripts=[all_leafs]  # 添加脚本树
    )
    tx.witnesses.append(TxWitnessInput([sig]))
    print(f"Path4 交易哈希: {tx.get_txid()}")


if __name__ == "__main__":
    main()