"""
Taproot Script Path 花费脚本
文件名: taproot_basic_reveal_scriptpath.py
作者: Aaron Zhang
日期: 2025-02-26
环境: Python 3.11, bitcoinutils (最新版), Testnet

功能概述:
本脚本实现了一个 Taproot 地址的 Script Path 花费：
- 使用 preimage "helloworld" 通过脚本条件（OP_SHA256 <hash> OP_EQUALVERIFY OP_TRUE）解锁资金。
- 从一个 Taproot 输入（带脚本树）花费，输出到 Alice 的简单 Taproot 地址。
脚本验证了 preimage 的 SHA256 哈希是否匹配预定义值，成功后转移资金。

运行记录:
- 输入: e9b354b2f4b71fa2e21479c13c22e82978ac1240a4bb000c471ca8bbcc6331d3:0
  - 金额: 0.00001100 tBTC (1100 聪)
  - 地址: tb1p53ncq9ytax924ps66z6al3wfhy6a29w8h6xfu27xem06t98zkmvsakd43h
- 输出: tb1p060z97qusuxe7w6h8z0l9kam5kn76jur22ecel75wjlmnkpxtnls6vdgne
  - 金额: 0.00000800 tBTC (800 聪)
- TxId: 89379d0f21016f2f8a24bfe883a57918e6185550dc7258c3535f1e6c10db0d7f
- 结果: 成功 (2025-03-06)

Script Path 原理:
Taproot 地址由内部公钥 P 和脚本树 T 生成输出公钥 Q = P + H(P || T) * G，其中:
- P: Alice 的公钥 (internal_pub)。
- T: 脚本树的 Merkle 根 (H(tr_script))。
- H: Taproot 的 tagged hash 函数。
- G: 椭圆曲线生成点。
Script Path 花费通过提供 preimage 和控制块（Control Block）解锁资金：
- preimage: "helloworld" 的十六进制 (68656c6c6f776f726c64)。
- 脚本: OP_SHA256 <hash> OP_EQUALVERIFY OP_TRUE，验证 preimage 的 SHA256 是否匹配。
- 控制块: 包含脚本树的 Merkle 路径，证明脚本属于 Q。
见证数据包含 [preimage_hex, script_hex, control_block_hex]，无需私钥签名。

代码结构:
1. 导入模块: bitcoinutils 和 hashlib。
2. setup_network(): 设置 Testnet。
3. create_script(): 生成脚本路径 (preimage 条件)。
4. spend_script_path(): 通过 Script Path 花费。
5. main(): 主函数，运行 Script Path 测试。

使用说明:
- 替换 commit_txid 和 input_amount 为实际 UTXO。
- 确保 preimage 与脚本中的哈希匹配。
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
    
    # Alice 的密钥（仅用于生成地址）
    alice_private = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    alice_public = alice_private.get_public_key()
    
    # Preimage 和哈希
    preimage = "helloworld"
    preimage_hex = preimage.encode('utf-8').hex()  # 转换为十六进制
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    
    # 脚本路径
    tr_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])
    
    # Taproot 地址
    medium_sending_address = alice_public.get_taproot_address([[tr_script]])
    control_block = ControlBlock(alice_public, [[tr_script]], 0, is_odd=medium_sending_address.is_odd())
    
    # Commit 信息
    commit_txid = "e9b354b2f4b71fa2e21479c13c22e82978ac1240a4bb000c471ca8bbcc6331d3"
    input_amount = 0.000011  # 7000 satoshis
    output_amount = 0.000008
    # Script Path 花费
    txin = TxInput(commit_txid, 0)
    txout = TxOutput(to_satoshis(output_amount), alice_public.get_taproot_address().to_script_pub_key())
    tx = Transaction([txin], [txout], has_segwit=True)
    tx.witnesses.append(TxWitnessInput([preimage_hex, tr_script.to_hex(), control_block.to_hex()]))
    
    # 输出验证信息
    print(f"\n发送方的Taproot 地址: {medium_sending_address.to_string()}")
    print(f"发送方的ScriptPubKey: {medium_sending_address.to_script_pub_key().to_hex()}")
    print(f"\nInput Amount: {input_amount} tBTC ({to_satoshis(input_amount)} satoshis)")
    print(f"Output Amount: {output_amount} tBTC ({to_satoshis(output_amount)} satoshis)")
    print(f"Fee: {input_amount - output_amount} tBTC ({to_satoshis(input_amount) - to_satoshis(0.00001)} satoshis)")
    print(f"\nScript Path TxId: {tx.get_txid()}")
    print(f"\nRaw Tx: {tx.serialize()}")

if __name__ == "__main__":
    main()