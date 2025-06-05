"""
Bob + Hash 双脚本测试 - Commit 脚本

创建一个包含 hash script (helloworld) 和 Bob script 的双脚本 Taproot 地址
这样我们可以测试 Bob Script Path 是否正确工作

两种花费方式：
1. Script Path 1：任何人提供 preimage "helloworld" 来花费
2. Script Path 2：Bob 使用私钥签名来花费
3. Key Path：Alice 用私钥直接花费
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import PrivateKey
import hashlib

def main():
    # 设置测试网
    setup('testnet')
    
    # Alice 的密钥（内部密钥，Key Path）
    alice_private = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    alice_public = alice_private.get_public_key()
    
    # Bob 的密钥（Script Path 2）
    bob_private = PrivateKey('cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG')
    bob_public = bob_private.get_public_key()
    
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
    
    # Script Path 2: Bob 的签名脚本 - P2PK
    bob_script = Script([
        bob_public.to_x_only_hex(),
        'OP_CHECKSIG'
    ])
    
    print("=== Bob + Hash 双脚本 Taproot 地址信息 ===")
    print(f"Alice 私钥 (Key Path): {alice_private.to_wif()}")
    print(f"Alice 公钥 (Internal Key): {alice_public.to_hex()}")
    print(f"Bob 私钥 (Script Path 2): {bob_private.to_wif()}")
    print(f"Bob 公钥 (Script Path 2): {bob_public.to_hex()}")
    print(f"Bob 公钥 (x-only): {bob_public.to_x_only_hex()}")
    print(f"Preimage (Script Path 1): {preimage}")
    print(f"Preimage Hash: {preimage_hash}")
    
    # 按照验证的双脚本模式创建脚本树：平铺结构
    all_leafs = [hash_script, bob_script]
    
    # 创建 Taproot 地址
    taproot_address = alice_public.get_taproot_address(all_leafs)
    
    print(f"\nTaproot 地址: {taproot_address.to_string()}")
    
    print(f"\n=== 脚本路径信息 ===")
    print(f"Hash Script (索引 0): {hash_script}")
    print(f"Bob Script (索引 1): {bob_script}")
    
    print(f"\n=== 使用说明 ===")
    print("1. 向这个 Taproot 地址发送比特币")
    print("2. 可以通过以下三种方式花费:")
    print("   - Key Path: Alice 使用她的私钥直接签名")
    print("   - Script Path 1: 任何人提供正确的 preimage 'helloworld'")
    print("   - Script Path 2: Bob 使用他的私钥签名")
    
    print(f"\n=== 脚本树结构 ===")
    print("简单的双叶子树:")
    print("     ROOT")
    print("    /    \\")
    print("   /      \\")
    print("HASH     BOB")
    print("(hello  (P2PK)")
    print(" world)    ")
    
    # 验证 Control Block 构造
    from bitcoinutils.utils import ControlBlock
    
    print(f"\n=== Control Block 预览 ===")
    
    # Hash Script Control Block (索引 0)
    hash_cb = ControlBlock(alice_public, all_leafs, 0, is_odd=taproot_address.is_odd())
    print(f"Hash Script Control Block: {hash_cb.to_hex()}")
    
    # Bob Script Control Block (索引 1) 
    bob_cb = ControlBlock(alice_public, all_leafs, 1, is_odd=taproot_address.is_odd())
    print(f"Bob Script Control Block: {bob_cb.to_hex()}")
    
    print(f"\n✅ 准备就绪！向地址 {taproot_address.to_string()} 发送测试币后，")
    print("就可以测试 Bob Script Path 是否正确工作了！")

if __name__ == "__main__":
    main()