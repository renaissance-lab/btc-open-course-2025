# 01-commit.py
# 构造包含三种脚本的 Taproot 地址：哈希锁、多签和时间锁

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.utils import to_satoshis

import hashlib

def main():
    setup('testnet')

    # Alice 的内部私钥（用于 Taproot 地址）
    alice_priv = PrivateKey("cNqNeGWmf8MsMiuRi3qJj7okPBZvH3J2iEkC42sMcPYjmzCzdTCS")
    alice_pub = alice_priv.get_public_key()

    # Bob 和 Carol 的私钥，用于多签脚本
    bob_priv = PrivateKey("cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6")
    bob_pub = bob_priv.get_public_key()
    
    carol_priv = PrivateKey("cTeSvY5tq6CmPXcrr9puFsxgd3tHH2P5uoW3SYcMLVFBGhY2qExY")
    carol_pub = carol_priv.get_public_key()

    # Script 1: 哈希锁 - 验证 SHA256(preimage) == hash("secretword")
    preimage = "secretword"
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    hashlock_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])

    # Script 2: 多签脚本 - 需要 Bob 和 Carol 都签名
    multisig_script = Script([
        'OP_2', # 需要2个签名
        bob_pub.to_x_only_hex(),
        carol_pub.to_x_only_hex(),
        'OP_2', # 共2个公钥
        'OP_CHECKMULTISIG'
    ])

    # Script 3: 时间锁定脚本 - 在特定区块高度后可以由任何人花费
    # 使用相对时间锁 OP_CHECKSEQUENCEVERIFY，设置为100个区块
    # 4501843 + 100
    timelock_script = Script([
        100, # 100个区块的相对时间锁
        'OP_CHECKSEQUENCEVERIFY',
        'OP_DROP',
        'OP_TRUE'
    ])

    # 构建 Merkle Tree
    tree = [[hashlock_script, multisig_script], timelock_script]
    print("🌳 Merkle Tree:", tree)

    # 生成 Taproot 地址
    address = alice_pub.get_taproot_address(tree)
    print("🪙 请发送资金至该 Taproot 地址：", address.to_string())
    
    # 打印所有私钥和脚本信息，方便后续花费
    print("\n=== 密钥信息 ===")
    print(f"Alice 私钥 (Key Path): {alice_priv.to_wif()}")
    print(f"Alice 公钥 (Internal Key): {alice_pub.to_hex()}")
    print(f"Bob 私钥 (多签): {bob_priv.to_wif()}")
    print(f"Bob 公钥 (多签): {bob_pub.to_hex()}")
    print(f"Carol 私钥 (多签): {carol_priv.to_wif()}")
    print(f"Carol 公钥 (多签): {carol_pub.to_hex()}")
    
    print("\n=== 脚本信息 ===")
    print(f"Preimage (哈希锁): {preimage}")
    print(f"Preimage Hash: {preimage_hash}")
    print(f"哈希锁脚本 (索引 0): {hashlock_script}")
    print(f"多签脚本 (索引 1): {multisig_script}")
    print(f"时间锁脚本 (索引 2): {timelock_script}")
    
    print("\n=== 脚本树结构 ===")
    print("三叶子树:")
    print("     ROOT")
    print("    /    \\")
    print("   /      \\")
    print(" NODE    TIMELOCK")
    print(" /  \\")
    print("/    \\")
    print("HASH  MULTISIG")
    
    # 验证 Control Block 构造
    from bitcoinutils.utils import ControlBlock
    
    print(f"\n=== Control Block 预览 ===")
    
    # 哈希锁脚本 Control Block (索引 0)
    hash_cb = ControlBlock(alice_pub, tree, 0, is_odd=address.is_odd())
    print(f"哈希锁脚本 Control Block: {hash_cb.to_hex()}")
    
    # 多签脚本 Control Block (索引 1) 
    multisig_cb = ControlBlock(alice_pub, tree, 1, is_odd=address.is_odd())
    print(f"多签脚本 Control Block: {multisig_cb.to_hex()}")
    
    # 时间锁脚本 Control Block (索引 2)
    timelock_cb = ControlBlock(alice_pub, tree, 2, is_odd=address.is_odd())
    print(f"时间锁脚本 Control Block: {timelock_cb.to_hex()}")
    
    print(f"\n✅ 准备就绪！向地址 {address.to_string()} 发送测试币后，")
    print("就可以测试四种不同的花费方式了！")

if __name__ == '__main__':
    main()