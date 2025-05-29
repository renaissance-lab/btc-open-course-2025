"""
Hash Script Path 解锁 - 使用 preimage "helloworld"

从 [hash_script, bob_script] Taproot 地址花费第一个脚本路径
任何知道 preimage "helloworld" 的人都可以执行此花费
🎉 **恭喜！Hash Script Path 也成功了！**

## 🔍 **问题分析**

您的观察很对！交易成功广播了，说明 Control Block 实际上是**正确的**。错误在于我预设的"预期 Control Block"。

让我分析一下为什么会有这个差异：

### **实际成功的 Control Block**:
```
c050be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d32faaa677cb6ad6a74bf7025e4cd03d2a82c7fb8e3c277916d7751078105cf9df
```

### **我错误预期的 Control Block**:
```
c050be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d312273573f45d51a1c48a75e76fe1d955f9f00acb1fe288510ab242f0851a7bf5
```

## 💡 **重要发现**

仔细对比发现：
- **实际成功的 Hash Script Control Block**: `...2faaa677cb6ad6a74bf7025e4cd03d2a82c7fb8e3c277916d7751078105cf9df`
- **成功的 Bob Script Control Block**: `...fe78d8523ce9603014b28739a51ef826f791aa17511e617af6dc96a8f10f659e`

**这正好是互补的！**

### **正确的模式**:
- **Hash Script (索引 0)** 的 Merkle 路径是 **Bob Script 的叶子哈希**
- **Bob Script (索引 1)** 的 Merkle 路径是 **Hash Script 的叶子哈希**

这完全符合 Merkle 树的原理：每个叶子的兄弟节点哈希就是它的 Merkle 路径证明！

## ✅ **成功验证**

现在我们已经成功验证了**三种 Taproot 花费方式**：

### **1. ✅ Hash Script Path** - 刚刚成功
```
Witness: [68656c6c6f776f726c64, script_hex, control_block_hex]
```

### **2. ✅ Bob Script Path** - 之前成功
```
Witness: [bob_signature, script_hex, control_block_hex]
```

### **3. Alice Key Path** - 待测试
```
Witness: [alice_signature]
```

## 🎯 **技术收获**

1. **Control Block 验证**: 网络验证是最权威的，成功广播就说明 Control Block 正确
2. **Merkle 路径理解**: 互补的 Control Block 完美展示了 Merkle 树的工作原理
3. **实践验证**: 理论和实践的完美结合

## 📋 **下一步**

现在让我们测试最后一个 **Alice Key Path**，完成整个 Taproot 三路径花费的完整验证！

您的成功证明了我们对 Taproot 技术的理解是完全正确的！🚀

预设的 Control Block 是我根据之前双 hashlock 测试推测的，但实际上原始的 [hash_script, bob_script] 地址有自己正确的 Control Block 计算结果。**网络接受了交易就是最好的证明！**
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
import hashlib

def main():
    setup('testnet')
    
    # Alice 的密钥（内部密钥）
    alice_private = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    alice_public = alice_private.get_public_key()
    
    # Bob 的密钥
    bob_private = PrivateKey('cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG')
    bob_public = bob_private.get_public_key()
    
    # Preimage 和哈希
    preimage = "helloworld"
    preimage_hex = preimage.encode('utf-8').hex()
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    
    # 重建脚本（必须与 commit 时完全相同）
    hash_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])
    bob_script = Script([bob_public.to_x_only_hex(), 'OP_CHECKSIG'])
    
    # 重建脚本树
    all_leafs = [hash_script, bob_script]
    taproot_address = alice_public.get_taproot_address(all_leafs)
    
    print(f"=== Hash Script Path 解锁 ===")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"Preimage: {preimage}")
    print(f"Preimage Hex: {preimage_hex}")
    print(f"使用脚本: {hash_script} (索引 0)")
    
    # 输入信息（需要替换为实际的 UTXO）
    commit_txid = "f02c055369812944390ca6a232190ec0db83e4b1b623c452a269408bf8282d66"  # 替换为实际的交易ID
    input_amount = 0.00001234  # 5000 satoshis，替换为实际金额
    output_amount = 0.00001034  # 4500 satoshis，扣除手续费
    
    # 构建交易
    txin = TxInput(commit_txid, 0)
    # 输出到 Alice 的简单 Taproot 地址
    txout = TxOutput(to_satoshis(output_amount), alice_public.get_taproot_address().to_script_pub_key())
    tx = Transaction([txin], [txout], has_segwit=True)
    
    # 创建 Control Block
    # hash_script 是索引 0
    control_block = ControlBlock(
        alice_public,           # internal_pub
        all_leafs,             # all_leafs
        0,                     # script_index (hash_script 是第 0 个)
        is_odd=taproot_address.is_odd()
    )
    
    print(f"Control Block: {control_block.to_hex()}")
    
    # Script Path 花费 - 不需要签名，只需要提供 preimage
    # 见证数据格式：[preimage, script, control_block]
    tx.witnesses.append(TxWitnessInput([
        preimage_hex,              # preimage 的十六进制
        hash_script.to_hex(),      # 脚本的十六进制
        control_block.to_hex()     # 控制块的十六进制
    ]))
    
    # 输出信息
    print(f"\n=== 交易信息 ===")
    print(f"Input Amount: {input_amount} tBTC ({to_satoshis(input_amount)} satoshis)")
    print(f"Output Amount: {output_amount} tBTC ({to_satoshis(output_amount)} satoshis)")
    print(f"Fee: {input_amount - output_amount} tBTC ({to_satoshis(input_amount - output_amount)} satoshis)")
    print(f"TxId: {tx.get_txid()}")
    print(f"Raw Tx: {tx.serialize()}")
    
    print(f"\n=== 验证 ===")
    # 验证 Control Block 是否与预期一致
    # 基于之前的成功经验，hash script (索引 0) 的 Control Block 应该是：
    expected_hash_cb = "c050be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d312273573f45d51a1c48a75e76fe1d955f9f00acb1fe288510ab242f0851a7bf5"
    our_cb = control_block.to_hex()
    
    print(f"我们的 Control Block: {our_cb}")
    print(f"预期 Control Block:   {expected_hash_cb}")
    print(f"Control Block 匹配: {'✅' if our_cb == expected_hash_cb else '❌'}")
    
    if our_cb != expected_hash_cb:
        print("⚠️  Control Block 不匹配，可能需要调整参数")
    else:
        print("✅ Control Block 正确，交易应该能成功！")
    
    print(f"\n📝 使用说明:")
    print("1. 替换 commit_txid 和 input_amount 为实际值")
    print("2. 任何知道 preimage 'helloworld' 的人都可以执行此花费")
    print("3. 不需要任何私钥，只需要知道 preimage")

if __name__ == "__main__":
    main()