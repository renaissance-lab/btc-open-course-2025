"""
比特币多输入交易 - 高级技能与关键经验

1. Taproot 签名的特殊要求 (BIP 341)
   =========================================
   当交易包含 Taproot (P2TR) 输入时，签名该输入必须提供所有输入的脚本和金额信息。
   这是 BIP 341 规范的要求，不遵守这一点会导致"Invalid Schnorr signature"错误。
   
   错误方式:
   taproot_sig = taproot_private_key.sign_taproot_input(
       tx,
       taproot_index,
       [taproot_script],            # 错误: 只提供当前输入的脚本
       [to_satoshis(taproot_amount)] # 错误: 只提供当前输入的金额
   )
   
   正确方式:
   all_scripts = [input1_script, input2_script, ..., inputN_script]
   all_amounts = [to_satoshis(input1_amount), to_satoshis(input2_amount), ..., to_satoshis(inputN_amount)]
   
   taproot_sig = taproot_private_key.sign_taproot_input(
       tx,
       taproot_index,
       all_scripts,  # 提供所有输入的脚本
       all_amounts   # 提供所有输入的金额
   )

2. 三种不同类型输入的处理特点
   =========================================
   - Legacy (P2PKH) 输入:
     * 使用 sign_input() 方法签名
     * script_sig 包含签名和公钥: Script([legacy_sig, legacy_pub.to_hex()])
     * 没有见证数据，需要在 witnesses 列表中添加空占位符
   
   - SegWit (P2WPKH) 输入:
     * 使用 sign_segwit_input() 方法签名，需提供金额
     * script_sig 必须为空: Script([])
     * witnesses 包含签名和公钥: TxWitnessInput([segwit_sig, segwit_pub.to_hex()])
   
   - Taproot (P2TR) 输入:
     * 使用 sign_taproot_input() 方法签名，必须提供所有输入的脚本和金额
     * script_sig 必须为空: Script([])
     * witnesses 只包含 Schnorr 签名: TxWitnessInput([taproot_sig])
     * 不需要提供公钥，因为公钥已包含在输出脚本中

3. 见证数据的严格顺序
   =========================================
   见证数据必须与输入顺序严格一一对应:
   
   tx.witnesses = []
   tx.witnesses.append(TxWitnessInput([]))  # Legacy 输入的空占位符
   tx.witnesses.append(TxWitnessInput([segwit_sig, segwit_pub.to_hex()]))  # SegWit 见证
   tx.witnesses.append(TxWitnessInput([taproot_sig]))  # Taproot 见证
   
   如果输入顺序发生变化，见证数据的顺序也必须相应调整。

4. 多输入交易的签名顺序
   =========================================
   在多输入交易中，建议按以下顺序进行签名:
   
   1. 首先获取所有输入的脚本和金额信息
   2. 签名 Legacy 输入并设置 script_sig
   3. 签名 SegWit 输入 (script_sig 保持为空)
   4. 签名 Taproot 输入 (script_sig 保持为空)
   5. 按顺序设置所有输入的见证数据
   
   这样可以确保所有签名在创建时使用正确的交易状态。

5. 精确的 UTXO 信息至关重要
   =========================================
   交易的成功与否很大程度上取决于 UTXO 信息的准确性:
   
   - txid: 必须完全匹配, 不能有任何字符错误
   - vout: 必须是准确的输出索引 (从0开始计数)
   - 金额: 必须精确到 satoshi, 对 SegWit 和 Taproot 签名尤为重要
   
   为避免浮点精度问题，可以直接使用 satoshi 单位定义金额:
   legacy_satoshis = 1666
   legacy_amount = legacy_satoshis / 100_000_000  # 转换为 BTC 单位

6. 实用解决方案与常见问题
   =========================================
   - 如果出现 "Invalid Schnorr signature" 错误，首先检查 Taproot 签名是否提供了所有输入信息
   - 如果遇到复杂交易问题，考虑分解为多个简单交易，如 Legacy+SegWit → Taproot，然后 Taproot+Taproot → 最终地址
   - 使用最新版本的bitcoinutils或其他比特币库，以确保完全支持 Taproot 功能
   - 对于混合类型输入的高级交易，在广播前使用测试网进行充分测试

7. 性能与费用优化
   =========================================
   - Legacy 输入的成本最高，因为它们不受 SegWit 折扣
   - SegWit 输入因为隔离见证而获得大约75%的费用折扣
   - Taproot 输入因为使用 Schnorr 签名而更紧凑，通常费用最低
   - 交易费率应根据网络拥堵情况和紧急程度来设置

此经验总结基于实际成功构建的 Legacy + SegWit + Taproot 混合输入交易。
这些知识对更复杂的比特币脚本、支付通道和智能合约开发都非常有价值。
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import P2pkhAddress, P2wpkhAddress, P2trAddress, PrivateKey
from bitcoinutils.script import Script

def main():
    # 设置测试网
    setup('testnet')
    
    # ===== 输入1: Legacy P2PKH =====
    legacy_private_key = PrivateKey("cTnhHT1VVnvf7fAgDtVXAxbYdBC6BujGs4D1qN9P9oJm2UtKkBo7")
    legacy_pub = legacy_private_key.get_public_key()
    legacy_address = legacy_pub.get_address()
    
    # 从你提供的交易中获取 Legacy UTXO 信息
    legacy_txid = "6c4ea298da0b3f6557e780712bdd6a01da497e69208a15d146c41b1198fb1401"
    legacy_vout = 0  # 交易中第三个输出 (索引为2)
    legacy_amount = 0.00001666  # 1666 satoshis
    
    # ===== 输入2: SegWit P2WPKH =====
    segwit_private_key = PrivateKey("cThG187gvrsZwnzsmPZiHW58hrhGKrfMdhAtEZKQxmwgKEdQsQ2h")
    segwit_pub = segwit_private_key.get_public_key()
    segwit_address = segwit_pub.get_segwit_address()
    
    # 从你提供的交易中获取 SegWit UTXO 信息
    segwit_txid = "148c6ade6db11ba312117a4295a43a2a7bcef84b1c2d19fc1580b5b62699fa68"
    segwit_vout = 1  # 交易中第三个输出 (索引为2)
    segwit_amount = 0.00001888  # 1888 satoshis
    
    # ===== 输入3: Taproot P2TR =====
    taproot_private_key = PrivateKey("cPeon9fBsW2BxwJTALj3hGzh9vm8C52Uqsce7MzXGS1iFJkPF4AT")
    taproot_pub = taproot_private_key.get_public_key()
    taproot_address = taproot_pub.get_taproot_address()
    
    # 从你提供的交易中获取 Taproot UTXO 信息
    taproot_txid = "4c3d517088bfc29dafac9b4287a3736b228f97cb7cdff580cf8d2c8257e06a1b"
    taproot_vout = 1  # 交易中第三个输出 (索引为2)
    taproot_amount = 0.00001999  # 1999 satoshis
    
    # ===== 输出: Taproot P2TR =====
    output_address = P2trAddress("tb1p6vqhd6yh64ahqq0pn46fma6la9xrf4yvyft5vskgd595l5pdsavs72c22m")
    
    # 计算总输入金额
    total_input = legacy_amount + segwit_amount + taproot_amount
    fee = 0.00000500  # 手续费: 500 satoshis
    output_amount = total_input - fee
    
    print(f"=== 交易信息 ===")
    print(f"输入1 (Legacy): {int(legacy_amount * 100_000_000)} satoshis 从 {legacy_address.to_string()}")
    print(f"输入2 (SegWit): {int(segwit_amount * 100_000_000)} satoshis 从 {segwit_address.to_string()}")
    print(f"输入3 (Taproot): {int(taproot_amount * 100_000_000)} satoshis 从 {taproot_address.to_string()}")
    print(f"输出 (Taproot): {int(output_amount * 100_000_000)} satoshis 到 {output_address.to_string()}")
    print(f"手续费: {int(fee * 100_000_000)} satoshis")
    
    # 创建交易输入
    txin_legacy = TxInput(legacy_txid, legacy_vout)
    txin_segwit = TxInput(segwit_txid, segwit_vout)
    txin_taproot = TxInput(taproot_txid, taproot_vout)
    
    # 创建交易输出
    txout = TxOutput(to_satoshis(output_amount), output_address.to_script_pub_key())
    
    # 创建交易 (使用 has_segwit=True 因为有SegWit和Taproot输入)
    tx = Transaction([txin_legacy, txin_segwit, txin_taproot], [txout], has_segwit=True)
    
    print("\n=== 未签名的交易 ===")
    print(tx.serialize())
    
    # 收集所有输入的脚本和金额（用于Taproot签名）
    legacy_script = legacy_address.to_script_pub_key()
    segwit_script = segwit_address.to_script_pub_key()
    taproot_script = taproot_address.to_script_pub_key()
    
    all_scripts = [legacy_script, segwit_script, taproot_script]
    all_amounts = [to_satoshis(legacy_amount), to_satoshis(segwit_amount), to_satoshis(taproot_amount)]
    
    # ===== 签名各个输入 =====
    
    # 1. 签名 Legacy 输入
    legacy_sig = legacy_private_key.sign_input(tx, 0, legacy_script)
    txin_legacy.script_sig = Script([legacy_sig, legacy_pub.to_hex()])
    
    # 2. 签名 SegWit 输入
    segwit_sig = segwit_private_key.sign_segwit_input(
        tx,
        1,
        segwit_pub.get_address().to_script_pub_key(),  # 使用P2PKH脚本作为witness脚本
        to_satoshis(segwit_amount)
    )
    
    # SegWit 输入的 script_sig 必须为空
    txin_segwit.script_sig = Script([])
    
    # 3. 签名 Taproot 输入 - 关键是提供所有输入的脚本和金额
    taproot_sig = taproot_private_key.sign_taproot_input(
        tx,
        2,  # 第三个输入的索引
        all_scripts,  # 所有输入的脚本
        all_amounts   # 所有输入的金额
    )
    
    # Taproot 输入的 script_sig 必须为空
    txin_taproot.script_sig = Script([])
    
    # 设置见证数据
    tx.witnesses = []
    tx.witnesses.append(TxWitnessInput([]))  # Legacy 没有见证数据，添加空占位符
    tx.witnesses.append(TxWitnessInput([segwit_sig, segwit_pub.to_hex()]))  # SegWit 见证
    tx.witnesses.append(TxWitnessInput([taproot_sig]))  # Taproot 见证
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n=== 已签名的交易 ===")
    print(signed_tx)
    print("\nTxId:", tx.get_txid())
    
    # 打印交易详情
    print("\n=== 交易详情 ===")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")
    
    # 输出 HEX 格式的交易，可以直接用于广播
    print("\n=== 最终交易 HEX (用于广播) ===")
    print(signed_tx)
    
    return signed_tx

if __name__ == "__main__":
    main()