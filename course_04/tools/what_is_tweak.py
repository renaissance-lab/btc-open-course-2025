#!/usr/bin/env python3
"""
Taproot Tweak 术语精确定义演示
澄清 tweak 的精确含义和相关术语
"""

import hashlib

def tagged_hash(tag: str, msg: bytes) -> bytes:
    """BIP-340 Tagged Hash"""
    tag_hash = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(tag_hash + tag_hash + msg).digest()

def demonstrate_tweak_terminology():
    """演示 tweak 相关术语的精确定义"""
    
    print("=" * 70)
    print("Taproot Tweak 术语精确定义")
    print("=" * 70)
    
    # 测试数据
    internal_pubkey = bytes.fromhex("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798")
    merkle_root = hashlib.sha256(b"mock script tree").digest()
    
    print(f"内部公钥 P: {internal_pubkey.hex()}")
    print(f"Merkle Root: {merkle_root.hex()}")
    
    # 步骤分解
    print(f"\n" + "=" * 50)
    print("术语定义和计算步骤")
    print("=" * 50)
    
    # 1. 计算 tweak（标量值）
    tweak_scalar = tagged_hash("TapTweak", internal_pubkey + merkle_root)
    
    print(f"步骤 1: 计算 tweak（标量）")
    print(f"  公式: tweak = H(P || merkle_root)")
    print(f"  输入: P + merkle_root ({len(internal_pubkey + merkle_root)} bytes)")
    print(f"  输出: tweak = {tweak_scalar.hex()}")
    print(f"  类型: 32字节标量值")
    print(f"  含义: 这就是我们说的 'tweak'！")
    
    # 2. 椭圆曲线点运算（概念演示）
    print(f"\n步骤 2: 椭圆曲线运算（概念）")
    print(f"  公式: tweak_point = tweak * G")
    print(f"  说明: 将标量 tweak 乘以生成点 G")
    print(f"  结果: 得到椭圆曲线上的一个点")
    print(f"  注意: G 是固定的椭圆曲线生成点")
    
    # 3. 最终公钥
    print(f"\n步骤 3: 计算最终公钥")
    print(f"  公式: P' = P + tweak_point")
    print(f"  说明: 内部公钥 + tweak点 = 最终Taproot公钥")
    print(f"  术语: P' 被称为 'tweaked public key'")

def demonstrate_code_examples():
    """演示不同代码库中的术语使用"""
    
    print(f"\n" + "=" * 70)
    print("不同代码库中的术语使用")
    print("=" * 70)
    
    # bitcoinjs-lib 风格
    print("=== bitcoinjs-lib 风格 ===")
    print("""
function tapTweakHash(pubKey, merkleRoot) {
    // 这个函数返回的是 tweak（标量值）
    const tweak = taggedHash('TapTweak', Buffer.concat([pubKey, merkleRoot]));
    return tweak;  // 32字节标量
}

function tweakPublicKey(pubKey, tweak) {
    // 这个过程叫做 "tweaking"
    const tweakedPubKey = pubKey.add(G.multiply(tweak));
    return tweakedPubKey;  // 调整后的公钥
}
""")
    
    # bitcoinutils 风格
    print("=== bitcoinutils 风格 ===")
    print("""
def get_taproot_address(internal_pubkey, script_tree=None):
    # 计算 tweak 值
    if script_tree:
        merkle_root = calculate_merkle_root(script_tree)
        tweak = tagged_hash("TapTweak", internal_pubkey + merkle_root)
    else:
        tweak = tagged_hash("TapTweak", internal_pubkey)
    
    # 进行 tweaking 操作
    tweaked_pubkey = internal_pubkey + tweak * G
    return encode_taproot_address(tweaked_pubkey)
""")
    
    # BIP-341 规范语言
    print("=== BIP-341 规范术语 ===")
    print("""
Let t = tagged_hash("TapTweak", internal_pubkey || merkle_root)
    ↑ 这个 t 就是 "tweak"

Let Q = lift_x(internal_pubkey) + int(t) * G  
    ↑ 这个过程叫 "tweaking"
    ↑ 这个 Q 是 "tweaked public key"
""")

def demonstrate_practical_usage():
    """演示实际使用中的术语"""
    
    print(f"\n" + "=" * 70)
    print("实际使用中的术语示例")
    print("=" * 70)
    
    def calculate_taproot_components(internal_pubkey: bytes, merkle_root: bytes = None):
        """计算 Taproot 组件的标准实现"""
        
        if merkle_root is not None:
            tweak_input = internal_pubkey + merkle_root
            scenario = "Script-enabled Taproot"
        else:
            tweak_input = internal_pubkey
            scenario = "Key-only Taproot"
        
        # 这是 tweak（标量值）
        tweak = tagged_hash("TapTweak", tweak_input)
        
        return {
            'scenario': scenario,
            'tweak_input': tweak_input,
            'tweak': tweak,  # 这是关键的标量值
            'input_length': len(tweak_input)
        }
    
    # 测试用例
    test_pubkey = bytes.fromhex("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798")
    
    # 情况1：Key-only
    result1 = calculate_taproot_components(test_pubkey, None)
    print(f"=== {result1['scenario']} ===")
    print(f"Tweak input: {result1['tweak_input'].hex()}")
    print(f"Tweak value: {result1['tweak'].hex()}")
    print(f"Input length: {result1['input_length']} bytes")
    
    # 情况2：Script-enabled
    mock_merkle = hashlib.sha256(b"script").digest()
    result2 = calculate_taproot_components(test_pubkey, mock_merkle)
    print(f"\n=== {result2['scenario']} ===")
    print(f"Merkle root: {mock_merkle.hex()}")
    print(f"Tweak input: {result2['tweak_input'].hex()}")
    print(f"Tweak value: {result2['tweak'].hex()}")
    print(f"Input length: {result2['input_length']} bytes")
    
    print(f"\n=== 术语总结 ===")
    print(f"✓ tweak = H(P || merkle_root) [32字节标量]")
    print(f"✓ tweaking = 整个调整过程 P → P'")
    print(f"✓ tweaked key = 最终结果 P'")

def demonstrate_common_misconceptions():
    """演示常见误解"""
    
    print(f"\n" + "=" * 70)
    print("常见误解澄清")
    print("=" * 70)
    
    print("❌ 错误理解 1:")
    print("   'tweak' 指的是整个过程 P → P'")
    print("✅ 正确理解:")
    print("   'tweak' 是标量值 H(P || merkle_root)")
    print("   'tweaking' 才是整个过程")
    
    print(f"\n❌ 错误理解 2:")
    print("   'tweak' 是椭圆曲线上的点")
    print("✅ 正确理解:")
    print("   'tweak' 是标量（整数）")
    print("   'tweak * G' 才是椭圆曲线上的点")
    
    print(f"\n❌ 错误理解 3:")
    print("   'tweak' 就是最终的 Taproot 地址")
    print("✅ 正确理解:")
    print("   'tweak' 用于计算最终地址")
    print("   '最终地址' = encode(P + tweak * G)")
    
    # 数据类型澄清
    print(f"\n=== 数据类型澄清 ===")
    internal_pubkey = bytes(32)  # 模拟
    merkle_root = bytes(32)      # 模拟
    tweak = tagged_hash("TapTweak", internal_pubkey + merkle_root)
    
    print(f"internal_pubkey: {type(internal_pubkey)} ({len(internal_pubkey)} bytes)")
    print(f"merkle_root:     {type(merkle_root)} ({len(merkle_root)} bytes)")
    print(f"tweak:           {type(tweak)} ({len(tweak)} bytes) ← 标量值")
    print(f"tweak as int:    {int.from_bytes(tweak, 'big')} ← 整数表示")

def main():
    """主函数"""
    print("Taproot Tweak 术语精确定义演示")
    print("解答：tweak 到底是什么？")
    
    demonstrate_tweak_terminology()
    demonstrate_code_examples()
    demonstrate_practical_usage()
    demonstrate_common_misconceptions()
    
    print(f"\n" + "=" * 70)
    print("最终答案")
    print("=" * 70)
    print("问题：tweak 到底是什么？")
    print("答案：tweak = H(P || merkle_root)，是一个32字节的标量值")
    print("")
    print("完整公式解释：")
    print("  tweak = H(P || merkle_root)      ← 这是 tweak（标量）")
    print("  tweak_point = tweak * G          ← 椭圆曲线点乘")
    print("  P' = P + tweak_point             ← 点addition")
    print("")
    print("术语区分：")
    print("  • tweak       = 标量值 H(P || merkle_root)")
    print("  • tweaking    = 调整过程 P → P'")
    print("  • tweaked key = 最终结果 P'")

if __name__ == "__main__":
    main()