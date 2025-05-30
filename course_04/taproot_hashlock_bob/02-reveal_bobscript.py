"""
Bob Script Path 测试

基于双 hashlock 成功经验，测试 Bob Script Path 是否正确工作
使用新的 [hash_script, bob_script] 地址进行测试
# Bob Script Path 成功经验总结

## 🎯 关键成功因素

### 1. **地址一致性**
- **成功**: 使用的地址 `tb1p93c4wxsr87p88jau7vru83zpk6xl0shf5ynmutd9x0gxwau3tngq9a4w3z`
- **关键**: 这正是我们一直在尝试的原始地址！

### 2. **UTXO 状态**
- **失败原因**: 之前的 UTXO 可能已经被花费或状态异常
- **成功原因**: 使用了新的有效 UTXO (`8caddfad76a5b3a8595a522e24305dc20580ca868ef733493e308ada084a050c:1`)

### 3. **签名方法验证**
三种签名方法都生成了不同的签名，但第一种成功了：

#### ✅ 成功的方法 1 (标准方法):
```python
{
    "script_path": True,
    "tapleaf_script": bob_script,  # 单数
    "tweak": False
}
```
**签名**: `26a0eadca0bba3d1bb6f82b8e1f76e2d84038c97a92fa95cc0b9f6a6a59bac5f9977d7cb33dbd188b1b84e6d5a9447231353590578f358b2f18a66731f9f1c5c`

#### 方法 2 (无 tweak):
**签名**: `6c2255b37d0f51de87f3793c20efe8116d9c31f4107d22da857de1b0f06ba59a05a3b0b944ca9c11b2756729487010789a1bc4ca329cd0459ec7f115e302bc8d`

#### 方法 3 (复数形式):
**签名**: `2ad5600e8f17dbea4f08f7de904e100f6bb2986b6c91c53ff7e3fa5b73622d824c3cde203a526fb3db570a7caa3c99797fafee388ccdea5079501c59a35efe3a`

## 🔍 技术细节分析

### Control Block 完全正确
```
c050be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d3fe78d8523ce9603014b28739a51ef826f791aa17511e617af6dc96a8f10f659e
```
- ✅ 与双 hashlock 测试中成功的 helloaaron 完全相同
- ✅ 证明我们的 Control Block 构造方法完全正确

### 见证数据结构
```
Witness:
1. 26a0eadca0bba3d1bb6f82b8e1f76e2d84038c97a92fa95cc0b9f6a6a59bac5f9977d7cb33dbd188b1b84e6d5a9447231353590578f358b2f18a66731f9f1c5c  # Bob 的签名
2. 2084b5951609b76619a1ce7f48977b4312ebe226987166ef044bfb374ceef63af5ac  # Bob 脚本
3. c050be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d3fe78d8523ce9603014b28739a51ef826f791aa17511e617af6dc96a8f10f659e  # Control Block
```

### P2TR 脚本解码
```
OP_PUSHBYTES_32 84b5951609b76619a1ce7f48977b4312ebe226987166ef044bfb374ceef63af5 OP_CHECKSIG
```
- ✅ 正确的 P2PK 脚本格式
- ✅ Bob 的 x-only 公钥正确

## 💡 失败原因反思

### 之前失败的可能原因：
1. **UTXO 已被花费**: 可能我们一直在尝试花费已经不存在的 UTXO
2. **网络状态**: 测试网络的临时问题
3. **交易构造**: 可能之前的某些参数有细微错误

### 成功的关键：
1. **使用了新的有效 UTXO**
2. **保持了正确的 Control Block**
3. **标准的签名方法**

## 🏆 完整成功案例

### 三种 Taproot 花费方式全部验证成功：

#### 1. ✅ Key Path 花费
- **特点**: 只需要 Alice 签名，完全隐私
- **见证**: `[alice_signature]`

#### 2. ✅ Hash Script Path 花费  
- **特点**: 任何人提供 preimage 即可花费
- **见证**: `[preimage_hex, script_hex, control_block_hex]`

#### 3. ✅ Bob Script Path 花费
- **特点**: Bob 用私钥签名花费
- **见证**: `[bob_signature, script_hex, control_block_hex]`

## 📋 最佳实践总结

### Taproot 双脚本 Script Path 标准流程：

1. **脚本树构造**: `all_leafs = [script1, script2]` (平铺结构)
2. **地址生成**: `alice_public.get_taproot_address(all_leafs)`
3. **Control Block**: `ControlBlock(alice_public, all_leafs, script_index, is_odd=address.is_odd())`
4. **签名方式**: 
   ```python
   signature = private_key.sign_taproot_input(
       tx, 0, [scriptPubKey], [amount],
       script_path=True,
       tapleaf_script=script,  # 单数！
       tweak=False
   )
   ```
5. **见证数据**: `[signature, script.to_hex(), control_block.to_hex()]`

## 🎯 结论

**我们完全掌握了 Taproot 多路径花费的完整实现！**

这包括：
- ✅ Key Path 和 Script Path 的正确构造
- ✅ Control Block 的准确计算
- ✅ 双脚本树的标准实现
- ✅ 不同签名方式的正确使用

这是一个完整的 Taproot 高级功能实现，展示了比特币最新技术的强大灵活性！🚀
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
import hashlib

def main():
    setup('testnet')
    
    # Alice 和 Bob 的密钥
    alice_private = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    alice_public = alice_private.get_public_key()
    
    bob_private = PrivateKey('cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG')
    bob_public = bob_private.get_public_key()
    
    # 重建脚本
    preimage = "helloworld"
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    
    hash_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])
    bob_script = Script([bob_public.to_x_only_hex(), 'OP_CHECKSIG'])
    
    # 重建脚本树
    all_leafs = [hash_script, bob_script]
    taproot_address = alice_public.get_taproot_address(all_leafs)
    
    print(f"=== Bob Script Path 测试 ===")
    print(f"测试地址: {taproot_address.to_string()}")
    print(f"Bob 公钥 (x-only): {bob_public.to_x_only_hex()}")
    print(f"Bob Script: {bob_script}")
    
    # 输入信息（需要替换为实际的 UTXO）
    commit_txid = "8caddfad76a5b3a8595a522e24305dc20580ca868ef733493e308ada084a050c"  # 替换为新地址的 UTXO
    input_amount = 0.00001111  # 替换为实际金额
    output_amount = 0.00000900  # 扣除手续费
    
    # 构建交易
    txin = TxInput(commit_txid, 1)
    txout = TxOutput(to_satoshis(output_amount), bob_public.get_taproot_address().to_script_pub_key())
    tx = Transaction([txin], [txout], has_segwit=True)
    
    # 构造 Control Block（基于双 hashlock 成功经验，Bob Script 索引 = 1）
    control_block = ControlBlock(
        alice_public,           # internal_pub
        all_leafs,             # all_leafs
        1,                     # script_index (bob_script 是索引 1)
        is_odd=taproot_address.is_odd()
    )
    
    print(f"Control Block: {control_block.to_hex()}")
    
    # 测试多种签名方法
    signature_methods = [
        {
            "name": "标准方法",
            "params": {
                "script_path": True,
                "tapleaf_script": bob_script,
                "tweak": False
            }
        },
        {
            "name": "无 tweak",
            "params": {
                "script_path": True,
                "tapleaf_script": bob_script
            }
        },
        {
            "name": "复数形式",
            "params": {
                "script_path": True,
                "tapleaf_scripts": [bob_script],
                "tweak": False
            }
        }
    ]
    
    for i, method in enumerate(signature_methods):
        try:
            print(f"\n=== 尝试方法 {i+1}: {method['name']} ===")
            
            # 重新构建交易
            tx_test = Transaction([txin], [txout], has_segwit=True)
            
            # 构建签名参数
            sig_args = [
                tx_test,
                0,
                [taproot_address.to_script_pub_key()],
                [to_satoshis(input_amount)]
            ]
            
            # 添加方法特定参数
            sig_kwargs = method['params']
            
            # 执行签名
            sig = bob_private.sign_taproot_input(*sig_args, **sig_kwargs)
            print(f"签名成功: {sig}")
            
            # 构造见证数据
            tx_test.witnesses.append(TxWitnessInput([
                sig,
                bob_script.to_hex(),
                control_block.to_hex()
            ]))
            
            print(f"TxId: {tx_test.get_txid()}")
            print(f"Raw Tx: {tx_test.serialize()}")
            print(f"🚀 请尝试广播此交易 (方法 {i+1})")
            
        except Exception as e:
            print(f"方法 {i+1} 失败: {e}")
    
    print(f"\n=== 说明 ===")
    print("1. 先运行 bob_hash_commit_test.py 创建新的测试地址")
    print("2. 向新地址发送测试币")
    print("3. 替换 commit_txid 和 input_amount 为实际值")
    print("4. 运行此脚本测试 Bob Script Path")
    print("5. 如果成功，说明我们的方法完全正确！")

if __name__ == "__main__":
    main()