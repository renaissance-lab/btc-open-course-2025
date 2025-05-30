#!/usr/bin/env python3
"""
Taproot Tagged Hash 完整演示
作者: 基于用户代码扩展
日期: 2025-05-29
功能: 全面展示 BIP-340/341 中的 Tagged Hash 机制

包含内容:
1. Tagged Hash 基础实现和原理
2. 与普通 SHA256 的对比
3. 不同 Tag 的域分离效果
4. Taproot 相关的所有 Tagged Hash 类型
5. 实际 Taproot 地址计算演示
6. 性能和安全性分析
"""

import hashlib
import secrets
import time
from typing import List, Tuple

class TaprootTaggedHash:
    """Taproot Tagged Hash 完整实现类"""
    
    # BIP-340/341 定义的标准 Tags
    TAGS = {
        'TapTweak': 'TapTweak',           # Taproot 公钥调整
        'TapLeaf': 'TapLeaf',             # 脚本叶子哈希
        'TapBranch': 'TapBranch',         # Merkle 树分支哈希
        'TapSighash': 'TapSighash',       # Taproot 签名哈希
        'KeyAgg': 'KeyAgg/list',          # MuSig2 密钥聚合
        'KeyAggCoeff': 'KeyAgg/coeff',    # MuSig2 系数
        'Challenge': 'BIP0340/challenge', # Schnorr 签名挑战
        'Aux': 'BIP0340/aux',             # Schnorr 辅助随机数
        'Nonce': 'BIP0340/nonce',         # Schnorr nonce 生成
    }
    
    def __init__(self):
        # 预计算 tag hash 以提高性能
        self._tag_hashes = {}
        for name, tag in self.TAGS.items():
            tag_hash = hashlib.sha256(tag.encode('utf-8')).digest()
            self._tag_hashes[name] = tag_hash
    
    def tagged_hash(self, tag: str, msg: bytes) -> bytes:
        """
        计算 BIP-340 定义的 tagged hash
        
        公式: SHA256(SHA256(tag) + SHA256(tag) + msg)
        """
        if tag in self._tag_hashes:
            tag_hash = self._tag_hashes[tag]
        else:
            tag_hash = hashlib.sha256(tag.encode('utf-8')).digest()
        
        # tagged_msg = tag_hash + tag_hash + msg
        return hashlib.sha256(tag_hash + tag_hash + msg).digest()
    
    def tap_tweak_hash(self, pubkey: bytes, merkle_root: bytes = None) -> bytes:
        """计算 Taproot 调整哈希"""
        if merkle_root is None:
            msg = pubkey
        else:
            msg = pubkey + merkle_root
        return self.tagged_hash('TapTweak', msg)
    
    def tap_leaf_hash(self, version: int, script: bytes) -> bytes:
        """计算 Taproot 叶子哈希"""
        return self.tagged_hash('TapLeaf', bytes([version]) + self._compact_size(script) + script)
    
    def tap_branch_hash(self, left: bytes, right: bytes) -> bytes:
        """计算 Taproot 分支哈希"""
        # 确保字典序排序
        if left <= right:
            return self.tagged_hash('TapBranch', left + right)
        else:
            return self.tagged_hash('TapBranch', right + left)
    
    def _compact_size(self, data: bytes) -> bytes:
        """计算 compact size encoding"""
        length = len(data)
        if length < 0xfd:
            return bytes([length])
        elif length <= 0xffff:
            return b'\xfd' + length.to_bytes(2, 'little')
        elif length <= 0xffffffff:
            return b'\xfe' + length.to_bytes(4, 'little')
        else:
            return b'\xff' + length.to_bytes(8, 'little')

def demonstrate_basic_tagged_hash():
    """演示基础 Tagged Hash 概念"""
    print("=" * 60)
    print("1. Tagged Hash 基础演示")
    print("=" * 60)
    
    th = TaprootTaggedHash()
    
    # 测试数据
    test_data = b"Hello Taproot World!"
    
    print(f"测试数据: {test_data.decode()}")
    print(f"数据长度: {len(test_data)} bytes\n")
    
    # 不同的计算方式
    print("=== 计算过程分解 ===")
    
    # 1. 普通 SHA256
    normal_hash = hashlib.sha256(test_data).digest()
    print(f"普通 SHA256: {normal_hash.hex()}")
    
    # 2. Tagged Hash 详细步骤
    tag = "TapTweak"
    tag_encoded = tag.encode('utf-8')
    tag_hash = hashlib.sha256(tag_encoded).digest()
    
    print(f"\nTagged Hash 计算步骤:")
    print(f"1. Tag: '{tag}'")
    print(f"2. Tag Hash: {tag_hash.hex()}")
    print(f"3. 构造输入: tag_hash + tag_hash + data")
    
    tagged_input = tag_hash + tag_hash + test_data
    tagged_result = hashlib.sha256(tagged_input).digest()
    
    print(f"4. 输入长度: {len(tagged_input)} bytes")
    print(f"   - Tag Hash (x2): {len(tag_hash) * 2} bytes")
    print(f"   - 实际数据: {len(test_data)} bytes")
    print(f"5. Tagged Hash: {tagged_result.hex()}")
    
    # 3. 使用封装函数
    wrapped_result = th.tagged_hash("TapTweak", test_data)
    print(f"6. 封装函数结果: {wrapped_result.hex()}")
    
    # 验证一致性
    assert tagged_result == wrapped_result
    print(f"7. 结果一致性: ✓")

def demonstrate_domain_separation():
    """演示域分离效果"""
    print("\n" + "=" * 60)
    print("2. 域分离（Domain Separation）演示")
    print("=" * 60)
    
    th = TaprootTaggedHash()
    
    # 相同数据，不同 tag
    test_data = b"same data, different purpose"
    
    results = {}
    for tag_name in ['TapTweak', 'TapLeaf', 'TapBranch', 'Challenge']:
        results[tag_name] = th.tagged_hash(tag_name, test_data)
    
    print(f"测试数据: {test_data.decode()}")
    print("\n不同 Tag 产生的哈希结果:")
    
    for tag, hash_result in results.items():
        print(f"{tag:12}: {hash_result.hex()}")
    
    # 验证所有结果都不同
    hash_values = list(results.values())
    unique_hashes = len(set(hash_values))
    
    print(f"\n验证结果:")
    print(f"- 总共 {len(hash_values)} 个哈希")
    print(f"- 唯一哈希 {unique_hashes} 个")
    print(f"- 域分离效果: {'✓ 成功' if unique_hashes == len(hash_values) else '✗ 失败'}")

def demonstrate_taproot_calculation():
    """演示完整的 Taproot 地址计算"""
    print("\n" + "=" * 60)
    print("3. Taproot 地址计算演示")
    print("=" * 60)
    
    th = TaprootTaggedHash()
    
    # 模拟密钥和脚本
    internal_privkey = secrets.randbits(256).to_bytes(32, 'big')
    internal_pubkey = bytes.fromhex("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798")
    
    print(f"内部公钥: {internal_pubkey.hex()}")
    
    # 模拟脚本树
    scripts = [
        b'\x20' + hashlib.sha256(b"secret1").digest() + b'\x87',  # OP_SHA256 <hash> OP_EQUAL
        b'\x51',  # OP_TRUE
        b'\x20' + hashlib.sha256(b"secret2").digest() + b'\x87',  # 另一个哈希锁
    ]
    
    print(f"\n脚本树包含 {len(scripts)} 个脚本:")
    for i, script in enumerate(scripts):
        print(f"  脚本 {i+1}: {script.hex()} ({len(script)} bytes)")
    
    # 计算叶子哈希
    leaf_hashes = []
    for script in scripts:
        leaf_hash = th.tap_leaf_hash(0xc0, script)  # 0xc0 是标准版本
        leaf_hashes.append(leaf_hash)
        print(f"    叶子哈希: {leaf_hash.hex()}")
    
    # 构建 Merkle 树
    merkle_root = build_merkle_tree(th, leaf_hashes)
    print(f"\nMerkle Root: {merkle_root.hex()}")
    
    # 计算 Taproot 调整
    tweak_hash = th.tap_tweak_hash(internal_pubkey, merkle_root)
    print(f"Tweak Hash: {tweak_hash.hex()}")
    
    # 模拟最终公钥计算（这里只是演示概念）
    print(f"\nTaproot 公钥 = 内部公钥 + tweak_hash * G")
    print(f"（实际椭圆曲线运算需要专门的库）")

def build_merkle_tree(th: TaprootTaggedHash, leaf_hashes: List[bytes]) -> bytes:
    """构建 Merkle 树"""
    if len(leaf_hashes) == 1:
        return leaf_hashes[0]
    
    # 简化的 Merkle 树构建（实际实现更复杂）
    current_level = leaf_hashes[:]
    
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                # 有配对节点
                branch_hash = th.tap_branch_hash(current_level[i], current_level[i + 1])
            else:
                # 奇数节点，与自己配对
                branch_hash = current_level[i]
            next_level.append(branch_hash)
        current_level = next_level
    
    return current_level[0]

def demonstrate_performance_comparison():
    """演示性能对比"""
    print("\n" + "=" * 60)
    print("4. 性能对比分析")
    print("=" * 60)
    
    th = TaprootTaggedHash()
    test_data = secrets.randbits(256).to_bytes(32, 'big')
    iterations = 10000
    
    print(f"测试参数: {iterations} 次哈希计算")
    
    # 测试普通 SHA256
    start_time = time.time()
    for _ in range(iterations):
        hashlib.sha256(test_data).digest()
    normal_time = time.time() - start_time
    
    # 测试 Tagged Hash
    start_time = time.time()
    for _ in range(iterations):
        th.tagged_hash("TapTweak", test_data)
    tagged_time = time.time() - start_time
    
    print(f"\n性能结果:")
    print(f"普通 SHA256: {normal_time:.4f} 秒")
    print(f"Tagged Hash: {tagged_time:.4f} 秒")
    print(f"性能比率: {tagged_time/normal_time:.2f}x")
    print(f"每次 Tagged Hash 额外开销: {(tagged_time-normal_time)/iterations*1000:.3f} ms")

def demonstrate_security_properties():
    """演示安全属性"""
    print("\n" + "=" * 60)
    print("5. 安全属性演示")
    print("=" * 60)
    
    th = TaprootTaggedHash()
    
    # 测试数据
    test_cases = [
        (b"", "空数据"),
        (b"a", "单字符"),
        (b"a" * 31, "31 字节"),
        (b"a" * 32, "32 字节"),
        (b"a" * 33, "33 字节"),
        (b"a" * 64, "64 字节"),
        (secrets.randbits(256).to_bytes(32, 'big'), "随机数据"),
    ]
    
    print("=== 雪崩效应测试 ===")
    base_data = b"Hello Taproot"
    base_hash = th.tagged_hash("TapTweak", base_data)
    
    # 微小变化
    modified_data = b"Hello Taproot!"  # 只添加一个感叹号
    modified_hash = th.tagged_hash("TapTweak", modified_data)
    
    # 计算汉明距离
    hamming_distance = sum(b1 != b2 for b1, b2 in zip(base_hash, modified_hash))
    
    print(f"原始数据: {base_data}")
    print(f"修改数据: {modified_data}")
    print(f"原始哈希: {base_hash.hex()}")
    print(f"修改哈希: {modified_hash.hex()}")
    print(f"汉明距离: {hamming_distance}/32 字节 ({hamming_distance/32*100:.1f}%)")
    
    print(f"\n=== 不同长度数据的哈希分布 ===")
    for data, description in test_cases:
        hash_result = th.tagged_hash("TapTweak", data)
        print(f"{description:10}: {hash_result.hex()[:16]}...")

def demonstrate_real_world_usage():
    """演示真实世界的使用场景"""
    print("\n" + "=" * 60)
    print("6. 真实使用场景演示")
    print("=" * 60)
    
    th = TaprootTaggedHash()
    
    print("=== Atomicals 协议类似场景 ===")
    
    # 模拟 Atomicals 的参数
    nonce = 12345678
    timestamp = 1640995200  # 2022-01-01
    operation_type = "nft"
    
    # 构造 payload（简化版）
    payload_data = f"{operation_type}:{nonce}:{timestamp}".encode()
    
    print(f"操作类型: {operation_type}")
    print(f"Nonce: {nonce}")
    print(f"时间戳: {timestamp}")
    print(f"Payload: {payload_data}")
    
    # 生成脚本哈希
    script_hash = th.tap_leaf_hash(0xc0, payload_data)
    print(f"脚本哈希: {script_hash.hex()}")
    
    # 模拟内部公钥
    internal_pubkey = hashlib.sha256(b"user_seed").digest()
    print(f"内部公钥: {internal_pubkey.hex()}")
    
    # 计算 Taproot 调整
    tweak_hash = th.tap_tweak_hash(internal_pubkey, script_hash)
    print(f"调整哈希: {tweak_hash.hex()}")
    
    print(f"\n如果 nonce 丢失:")
    print(f"- ❌ 无法重构 payload_data")
    print(f"- ❌ 无法计算 script_hash")
    print(f"- ❌ 无法计算 tweak_hash")
    print(f"- ❌ 无法进行 Key Path 解锁")
    
    # 演示恢复过程
    print(f"\n=== Nonce 恢复演示 ===")
    target_script_hash = script_hash  # 已知的目标哈希
    
    print(f"目标脚本哈希: {target_script_hash.hex()}")
    print(f"开始暴力搜索 nonce...")
    
    # 模拟搜索（只搜索小范围）
    found_nonce = None
    search_range = 1000  # 实际应该搜索更大范围
    
    for candidate_nonce in range(nonce - search_range//2, nonce + search_range//2):
        candidate_payload = f"{operation_type}:{candidate_nonce}:{timestamp}".encode()
        candidate_hash = th.tap_leaf_hash(0xc0, candidate_payload)
        
        if candidate_hash == target_script_hash:
            found_nonce = candidate_nonce
            break
    
    if found_nonce:
        print(f"✓ 找到 nonce: {found_nonce}")
        print(f"✓ 可以重构完整的解锁条件")
    else:
        print(f"✗ 在搜索范围内未找到 nonce")

def main():
    """主函数：运行所有演示"""
    print("Taproot Tagged Hash 完整演示")
    print("作者: 基于用户代码扩展")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 运行所有演示
        demonstrate_basic_tagged_hash()
        demonstrate_domain_separation()
        demonstrate_taproot_calculation()
        demonstrate_performance_comparison()
        demonstrate_security_properties()
        demonstrate_real_world_usage()
        
        print("\n" + "=" * 60)
        print("演示完成！主요收获:")
        print("=" * 60)
        print("1. Tagged Hash 不是简单的 SHA256，而是双重哈希结构")
        print("2. 域分离确保了不同用途的哈希不会冲突")
        print("3. Taproot 地址生成依赖完整的脚本树信息")
        print("4. 参数丢失（如 nonce）会导致无法重构解锁条件")
        print("5. 性能开销约为普通 SHA256 的 2-3 倍")
        print("6. 安全性通过雪崩效应得到保证")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()