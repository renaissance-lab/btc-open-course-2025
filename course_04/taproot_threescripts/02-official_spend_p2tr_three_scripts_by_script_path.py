# Copyright (C) 2018-2025 The python-bitcoin-utils developers
#
# This file is part of python-bitcoin-utils
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoin-utils, including this file, may be copied,
# modified, propagated, or distributed except according to the terms contained
# in the LICENSE file.

# ===============================================
# 🟩 Taproot Script Path Spend 教学注释
# 文件名：spend_p2tr_three_scripts_by_script_path.py
# ===============================================

"""
本示例演示了如何构造一个 Taproot 地址，其中包含三个脚本（script A, B, C），
并通过 Script Path 花费其中一个指定的脚本（本例中为 script B）。

我们使用的是 python-bitcoin-utils 库，它在构造 Taproot 树和 Control Block 上提供了高度自由度，
但也要求我们对 Taproot Merkle Tree 的规则有清晰理解。

====================
📌 Taproot Script Path Spend 核心原理：
====================

一个 Taproot 地址可由以下两部分构成：

1. 内部公钥（Internal Public Key） —— P
2. 可选的 Merkle Tree 脚本树（Script Tree） —— M

Taproot address 的最终输出地址为：

    Taproot Address = tweaked(P + hash(M))

当我们使用 script path 花费 Taproot 输出时，需要提供：

1. 被花费的脚本（tapleaf）—— leaf_script
2. 对该脚本 hash 的签名（signature）
3. 一个 control block，用于证明该脚本属于 Merkle Tree

Bitcoin 节点将使用 control block 和 tapleaf script，还原出 Taproot 地址（即验证“你不是伪造路径”）。

====================
✅ 本例成功的关键步骤：
====================

1. 正确构造 Merkle Tree：
    - 使用列表嵌套结构，确定每个脚本在树中的顺序与位置。
    - 本例中结构为： [[script_A, script_B], script_C]
        -> script_B 是左子树的右子节点，索引为 1。

2. 正确选择目标脚本（script B）：
    - 你必须用该脚本所对应的私钥来生成签名。
    - 同时你要知道这个脚本在树中的索引（index = 1）。

3. 正确构造 ControlBlock：
    - 使用 `ControlBlock(internal_pubkey, script_tree, leaf_index, is_odd)`
    - ⚠️ 坑点：`is_odd` 必须使用你要花费的地址（即输入地址）的奇偶性：
        ✅ `from_address.is_odd()`，❌ `to_address.is_odd()`

4. 正确构造 Witness：
    - Witness stack 必须为：
        [signature, script, control_block]
    - ⚠️ 错误构造 witness 会导致以下典型报错：
        - `witness program hash mismatch`
        - `invalid Schnorr signature`
        - `non-mandatory-script-verify-flag`

====================
🧱 常见坑位及其含义：
====================

1. ❌ 使用错误的 leaf index 构造 control block：
    - 即使签名正确，control block hash 路径不对，会还原出错误地址。
    - 会导致：`witness program hash mismatch`

2. ❌ 用了错误的奇偶性 is_odd：
    - 控制块最后一个字节用于还原 Taproot 公钥，需要与原始地址匹配。
    - `ControlBlock(..., is_odd=to_address.is_odd())` 是典型错误，必须是 `from_address`

3. ❌ 签名脚本不属于该 Taproot：
    - 即 `tapleaf_script` 没有出现在你构造的 script_tree 中。

4. ❌ 花费了带 script 的 Taproot 地址，但误用 key path 签名：
    - 没有 tweak 的私钥不能用于 keypath 花费包含 merkle root 的地址。

====================
🧪 建议的调试方法：
====================

- 使用 `bitcoin-cli -testnet decoderawtransaction` 查看 Witness 是否包含正确结构。
- 使用 `gettxout` 确认 UTXO 是否未花费。
- 使用 `validateaddress` 验证 Taproot 地址的内部公钥。
- 用 `assert cb.get_tweaked_pubkey() == from_address.get_pubkey()` 验证控制块正确性。

====================
✨ 最佳实践建议：
====================

- 用结构清晰的 tree（如 [[A, B], C]）并手动追踪索引位置。
- 将 `ControlBlock(...)` 的构造封装为工具函数，以避免 index 和奇偶性错用。
- 开发时优先使用 regtest 模式，便于定位 bug。
- 测试三种脚本都能花费、顺序调换脚本验证 Merkle Root 是否一致。

"""

# 你可以将本注释放在主函数 `main()` 之前作为教学头注释

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
from bitcoinutils.hdwallet import HDWallet


def main():
    # always remember to setup the network
    setup("testnet")

    #######################
    # Construct the input #
    #######################

    # get an HDWallet wrapper object by extended private key and path
    xprivkey = (
        "tprv8ZgxMBicQKsPdQR9RuHpGGxSnNq8Jr3X4WnT6Nf2eq7FajuXyBep5KWYpYEixxx5XdTm1N"
        "tpe84f3cVcF7mZZ7mPkntaFXLGJD2tS7YJkWU"
    )
    path = "m/86'/1'/0'/0/7"
    hdw = HDWallet(xprivkey, path)
    internal_priv = hdw.get_private_key()
    print("From Private key:", internal_priv.to_wif())
    internal_pub = internal_priv.get_public_key()
    print("From Public key:", internal_pub.to_hex())

    # taproot script is a simple P2PK with the following keys
    privkey_tr_script_A = PrivateKey(
        "cSW2kQbqC9zkqagw8oTYKFTozKuZ214zd6CMTDs4V32cMfH3dgKa"
    )
    pubkey_tr_script_A = privkey_tr_script_A.get_public_key()
    tr_script_p2pk_A = Script([pubkey_tr_script_A.to_x_only_hex(), "OP_CHECKSIG"])

    # taproot script B is a simple P2PK with the following keys
    privkey_tr_script_B = PrivateKey(
        "cSv48xapaqy7fPs8VvoSnxNBNA2jpjcuURRqUENu3WVq6Eh4U3JU"
    )
    pubkey_tr_script_B = privkey_tr_script_B.get_public_key()
    tr_script_p2pk_B = Script([pubkey_tr_script_B.to_x_only_hex(), "OP_CHECKSIG"])

    # taproot script C is a simple P2PK with the following keys
    privkey_tr_script_C = PrivateKey(
        "cRkZPNnn3jdr64o3PDxNHG68eowDfuCdcyL6nVL4n3czvunuvryC"
    )
    pubkey_tr_script_C = privkey_tr_script_C.get_public_key()
    tr_script_p2pk_C = Script([pubkey_tr_script_C.to_x_only_hex(), "OP_CHECKSIG"])

    # tapleafs in order
    #                  TB_ABC
    #                  /    \
    #                 /      \
    #              TB_AB      \
    #               / \        \
    #              /   \        \
    #            TL_A TL_B     TL_C
    all_leafs = [[tr_script_p2pk_A, tr_script_p2pk_B], tr_script_p2pk_C]

    # taproot script path address
    from_address = internal_pub.get_taproot_address(all_leafs)
    print("From Taproot script address", from_address.to_string())

    # UTXO of from_address
    txid = "e00108a7c07699dc8202897df556e57f21b3cf2c7be88f5ed11ba371e918719d"
    vout = 0

    # create transaction input from tx id of UTXO
    tx_in = TxInput(txid, vout)

    # all amounts are needed to sign a taproot input
    # (depending on sighash)
    amount = to_satoshis(0.00002000)
    amounts = [amount]

    # all scriptPubKeys (in hex) are needed to sign a taproot input
    # (depending on sighash but always of the spend input)
    scriptPubkey = from_address.to_script_pub_key()
    utxos_scriptPubkeys = [scriptPubkey]

    ########################
    # Construct the output #
    ########################

    hdw.from_path("m/86'/1'/0'/0/5")
    to_priv = hdw.get_private_key()
    print("To Private key:", to_priv.to_wif())

    to_pub = to_priv.get_public_key()
    print("To Public key:", to_pub.to_hex())

    # taproot key path address
    to_address = to_pub.get_taproot_address()
    print("To Taproot address:", to_address.to_string())

    # create transaction output
    tx_out = TxOutput(to_satoshis(0.00001500), to_address.to_script_pub_key())

    # create transaction without change output - if at least a single input is
    # segwit we need to set has_segwit=True
    tx = Transaction([tx_in], [tx_out], has_segwit=True)

    print("\nRaw transaction:\n" + tx.serialize())

    print("\ntxid: " + tx.get_txid())
    print("\ntxwid: " + tx.get_wtxid())

    # sign taproot input
    # to create the digest message to sign in taproot we need to
    # pass all the utxos' scriptPubKeys, their amounts and taproot script
    # we sign with the private key corresponding to the script - no key
    # tweaking required
    sig = privkey_tr_script_B.sign_taproot_input(
        tx,
        0,
        utxos_scriptPubkeys,
        amounts,
        script_path=True,
        tapleaf_script=tr_script_p2pk_B,
        tweak=False,
    )

    # we need to provide the merkle path (in bytes)
    control_block = ControlBlock(internal_pub, all_leafs, 1, is_odd=from_address.is_odd())

    tx.witnesses.append(
        TxWitnessInput([sig, tr_script_p2pk_B.to_hex(), control_block.to_hex()])
    )

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + tx.serialize())

    print("\nTxId:", tx.get_txid())
    print("\nTxwId:", tx.get_wtxid())

    print("\nSize:", tx.get_size())
    print("\nvSize:", tx.get_vsize())


if __name__ == "__main__":
    main()
