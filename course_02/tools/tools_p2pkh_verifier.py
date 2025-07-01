#!/usr/bin/env python3
"""
比特币P2PKH地址验证工具 - 使用bitcoinlib库的版本
需要安装: pip install bitcoin
"""

# 如果没有安装bitcoin库，可以使用以下简化版本
import hashlib
import binascii

# 简化的辅助函数
def sha256(data):
    return hashlib.sha256(data).digest()

def ripemd160(data):
    return hashlib.new('ripemd160', data).digest()

def hash160(data):
    return ripemd160(sha256(data))

# Base58编码字符集
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(data):
    """Base58编码"""
    num = int.from_bytes(data, 'big')
    if num == 0:
        return BASE58_ALPHABET[0]
    
    result = []
    while num > 0:
        num, remainder = divmod(num, 58)
        result.append(BASE58_ALPHABET[remainder])
    
    # 处理前导零
    for byte in data:
        if byte == 0:
            result.append(BASE58_ALPHABET[0])
        else:
            break
    
    return ''.join(reversed(result))

def base58_decode(s):
    """Base58解码"""
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)
    
    # 转换为字节
    num_bytes = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    
    # 处理前导1
    for char in s:
        if char == '1':
            num_bytes = b'\x00' + num_bytes
        else:
            break
    
    return num_bytes

class P2PKHVerifier:
    """P2PKH地址验证器"""
    
    @staticmethod
    def pubkey_to_hash160(pubkey_hex):
        """
        将公钥转换为HASH160
        输入: 十六进制格式的公钥
        输出: HASH160的十六进制字符串
        """
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        return hash160(pubkey_bytes).hex()
    
    @staticmethod
    def hash160_to_address(hash160_hex, network='testnet'):
        """
        将HASH160转换为比特币地址
        输入: HASH160的十六进制字符串, 网络类型
        输出: 比特币地址
        """
        hash160_bytes = bytes.fromhex(hash160_hex)
        
        # 添加版本前缀
        if network == 'mainnet':
            version = b'\x00'  # P2PKH主网
        else:
            version = b'\x6f'  # P2PKH测试网
        
        # 创建payload
        payload = version + hash160_bytes
        
        # 计算校验和
        checksum = sha256(sha256(payload))[:4]
        
        # 组合并编码
        return base58_encode(payload + checksum)
    
    @staticmethod
    def address_to_hash160(address):
        """
        从地址提取HASH160
        输入: 比特币地址
        输出: 解码后的信息字典
        """
        # Base58解码
        decoded = base58_decode(address)
        
        # 提取各部分
        version = decoded[0:1]
        hash160 = decoded[1:21]
        checksum = decoded[21:25]
        
        # 验证校验和
        payload = version + hash160
        expected_checksum = sha256(sha256(payload))[:4]
        
        return {
            'network': 'testnet' if version == b'\x6f' else 'mainnet',
            'version': version.hex(),
            'hash160': hash160.hex(),
            'checksum_valid': checksum == expected_checksum
        }

def run_verification_examples():
    """运行验证示例"""
    verifier = P2PKHVerifier()
    
    # 您提供的数据
    examples = [
        {
            'name': '第一个公钥 (n14GXhPZ4GWMmojsZr53LfHVNxCekQBaSH)',
            'pubkey': '021d85b17a74b2a1cf2152907c908ea1e5d38616f1f1c345af75d23c38b3ad4449',
            'expected_hash160': 'd65681b79db2601673ac8c5b5a4939bd11b00e13',
            'expected_address': 'n14GXhPZ4GWMmojsZr53LfHVNxCekQBaSH'
        },
        {
            'name': '第二个公钥 (mkMgewbz1vEvuA5hFfNe6EsnPbvtnFj5LH)',
            'pubkey': '033d5c62720a026ee26bdf238f3808a6825e8eebd9a7b7627eaf6402164e7f4ec2',
            'expected_hash160': '3517d46b972af88b6064090cfb44e346df0fbab1',
            'expected_address': 'mkMgewbz1vEvuA5hFfNe6EsnPbvtnFj5LH'
        }
    ]
    
    for example in examples:
        print(f"\n{'='*60}")
        print(f"验证: {example['name']}")
        print('='*60)
        
        # 步骤1: 公钥 -> HASH160
        print(f"\n1. 公钥 -> HASH160")
        print(f"   输入公钥: {example['pubkey']}")
        calculated_hash160 = verifier.pubkey_to_hash160(example['pubkey'])
        print(f"   计算HASH160: {calculated_hash160}")
        print(f"   期望HASH160: {example['expected_hash160']}")
        print(f"   匹配: {'✓' if calculated_hash160 == example['expected_hash160'] else '✗'}")
        
        # 步骤2: HASH160 -> 地址
        print(f"\n2. HASH160 -> 地址")
        calculated_address = verifier.hash160_to_address(calculated_hash160, 'testnet')
        print(f"   计算地址: {calculated_address}")
        print(f"   期望地址: {example['expected_address']}")
        print(f"   匹配: {'✓' if calculated_address == example['expected_address'] else '✗'}")
        
        # 步骤3: 地址 -> HASH160 (反向验证)
        print(f"\n3. 地址 -> HASH160 (反向验证)")
        decoded = verifier.address_to_hash160(example['expected_address'])
        print(f"   从地址解码:")
        print(f"     网络: {decoded['network']}")
        print(f"     HASH160: {decoded['hash160']}")
        print(f"     校验和有效: {'✓' if decoded['checksum_valid'] else '✗'}")
        print(f"   反向验证匹配: {'✓' if decoded['hash160'] == calculated_hash160 else '✗'}")

def interactive_mode():
    """交互式模式"""
    verifier = P2PKHVerifier()
    
    print("\n" + "="*60)
    print("交互式P2PKH验证工具")
    print("="*60)
    
    while True:
        print("\n选择操作:")
        print("1. 公钥 -> HASH160 -> 地址")
        print("2. 地址 -> HASH160")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == '1':
            pubkey = input("请输入公钥 (十六进制): ").strip()
            if pubkey:
                try:
                    hash160 = verifier.pubkey_to_hash160(pubkey)
                    address_testnet = verifier.hash160_to_address(hash160, 'testnet')
                    address_mainnet = verifier.hash160_to_address(hash160, 'mainnet')
                    
                    print(f"\n结果:")
                    print(f"HASH160: {hash160}")
                    print(f"测试网地址: {address_testnet}")
                    print(f"主网地址: {address_mainnet}")
                except Exception as e:
                    print(f"错误: {e}")
        
        elif choice == '2':
            address = input("请输入比特币地址: ").strip()
            if address:
                try:
                    decoded = verifier.address_to_hash160(address)
                    print(f"\n结果:")
                    print(f"网络: {decoded['network']}")
                    print(f"HASH160: {decoded['hash160']}")
                    print(f"版本: {decoded['version']}")
                    print(f"校验和有效: {'✓' if decoded['checksum_valid'] else '✗'}")
                except Exception as e:
                    print(f"错误: {e}")
        
        elif choice == '3':
            print("退出程序")
            break
        
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    # 运行示例验证
    run_verification_examples()
    
    # 询问是否进入交互模式
    print("\n" + "="*60)
    if input("是否进入交互模式? (y/n): ").lower() == 'y':
        interactive_mode()