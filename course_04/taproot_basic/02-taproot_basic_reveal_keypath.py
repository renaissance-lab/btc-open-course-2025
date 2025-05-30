"""
Taproot 双路径花费脚本 - Key Path 和 Script Path
文件名: taproot_basic_reveal_keypath.py / taproot_basic_reveal_scriptpath.py
作者: Aaron Zhang
日期: 2025-02-26
环境: Python 3.11, bitcoinutils (最新版), Testnet

功能概述:
本脚本实现了一个 Taproot 地址的双路径花费：
- Key Path: 使用 Alice 的私钥直接签名花费。
- Script Path: 使用 preimage "helloworld" 通过脚本条件花费。
脚本从一个 Taproot 输入（带脚本树）花费资金，输出到另一个 Taproot 地址。

运行记录:
1. Key Path:
   - 输入: f4a0233be3dcdc3764646c3d2c7d02e29d38b3449aca98234a91e08a9c96a228:0 (3000 聪)
   - 输出: tb1p060z97qusuxe7w6h8z0l9kam5kn76jur22ecel75wjlmnkpxtnls6vdgne (2000 聪)
   - TxId: 2a13de71b3eb9c5845bc9aed56de0efd7d8f1e5e02debb0e9b3464a4ad940d05
   - 结果: 成功 (2025-02-26)
2. Script Path:
   - 输入: 9e193d8c5b4ff4ad7cb13d196c2ecc210d9b0ec144bb919ac4314c1240629886:0 (5000 聪)
   - 输出: tb1p060z97qusuxe7w6h8z0l9kam5kn76jur22ecel75wjlmnkpxtnls6vdgne (4000 聪)
   - TxId: 68f7c8f0ab6b3c6f7eb037e36051ea3893b668c26ea6e52094ba01a7722e604f
   - 结果: 成功 (2025-02-26)

Key Path 原理:
Taproot 地址由内部公钥 P 和脚本树 T 生成输出公钥 Q = P + H(P || T) * G，其中:
- P: Alice 的公钥 (internal_pub)。
- T: 脚本树的 Merkle 根 (H(tr_script))。
- H: Taproot 的 tagged hash 函数。
- G: 椭圆曲线生成点。
Key Path 花费直接使用私钥 d (对应 P) 签名，但需调整为 d' = d + H(P || T)，以匹配 Q。
签名需要:
- utxos_scriptPubkeys: 输入的 ScriptPubKey 列表。
- amounts: 输入金额列表。
- tapleaf_scripts: 脚本树（即使不用 Script Path，也需提供以计算 tweak）。

代码结构:
1. 导入模块: bitcoinutils 和 hashlib。
2. setup_network(): 设置 Testnet。
3. create_script(): 生成脚本路径 (preimage 条件)。
4. spend_key_path(): 通过 Key Path 花费。
5. spend_script_path(): 通过 Script Path 花费。
6. main(): 主函数，运行双路径测试。

使用说明:
- 替换 commit_txid 和 input_amount 为实际 UTXO。
- 确保 bitcoinutils 最新版本 (pip install bitcoin-utils --upgrade)。
- 清理缓存 (find . -name "*.pyc" -delete) 避免旧代码干扰。
- 广播 Raw Tx 到 https://mempool.space/testnet/tx/push。
"""
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
import hashlib

def main():
    setup('testnet')
    
    # Alice 的密钥
    alice_private = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    alice_public = alice_private.get_public_key()
    
    # Preimage 和哈希
    preimage = "helloworld"
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    
    # 脚本路径
    tr_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])
    
    # sender 的 Taproot 地址
    medium_sending_address = alice_public.get_taproot_address([[tr_script]])
    
    # Commit 信息
    commit_txid = "4fd83128fb2df7cd25d96fdb6ed9bea26de755f212e37c3aa017641d3d2d2c6d"
    input_amount = 0.00003900  # 3900 satoshis
    
    output_amount = 0.00003700  # 3700 satoshis
    # Key Path 花费
    txin = TxInput(commit_txid, 0)
    receiving_address_pubkey =  alice_public.get_taproot_address().to_script_pub_key()
    txout = TxOutput(to_satoshis(output_amount), receiving_address_pubkey)
    tx = Transaction([txin], [txout], has_segwit=True)
    sig = alice_private.sign_taproot_input(
        tx,
        0,
        [medium_sending_address.to_script_pub_key()],
        [to_satoshis(input_amount)],
        script_path=False,
        tapleaf_scripts=[tr_script]  # 添加脚本树
    )
    tx.witnesses.append(TxWitnessInput([sig]))
    
    # 输出验证信息
    print(f"\n发送方的Taproot 地址: {medium_sending_address.to_string()}")
    print(f"发送方的ScriptPubKey: {medium_sending_address.to_script_pub_key().to_hex()}")
    print(f"接收方的ScriptPubKey: {receiving_address_pubkey.to_hex()}")
    print(f"接收方的Taproot 地址,本代码是又发回了alice的地址: {alice_public.get_taproot_address().to_string()}")
    print(f"\nInput Amount: {input_amount} tBTC ({to_satoshis(input_amount)} satoshis)")
    print(f"Output Amount:  tBTC ({to_satoshis(output_amount)} satoshis)")
    print(f"Fee: {input_amount - output_amount} tBTC ({to_satoshis(input_amount) - to_satoshis(output_amount)} satoshis)")
    print(f"\nUnsigned Tx: {tx.serialize()}")
    print(f"\nSchnorr Signature: {sig}")
    print(f"\nKey Path TxId: {tx.get_txid()}")
    print(f"Raw Tx: {tx.serialize()}")

if __name__ == "__main__":
    main()