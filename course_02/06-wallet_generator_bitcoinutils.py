"""
比特币钱包生成器 - bitcoinutils 版本

📌 主要功能：
1. 生成比特币私钥（HEX 格式）和 WIF（Base58Check 编码）
2. 计算公钥（压缩和未压缩格式）
3. 可以生成 4 种比特币地址（本例产生3种：P2PKH,P2WPKH,P2TR）
   - **P2PKH (Legacy)**：Base58 编码，1 开头
   - **P2SH (兼容 SegWit)**：Base58 编码，3 开头
   - **P2WPKH (原生 SegWit)**：Bech32 编码，bc1q 开头
   - **P2TR (Taproot)**：Bech32m 编码，bc1p 开头

📌 地址的字节数：
| **地址类型** | **编码格式** | **原始数据大小** | **最终地址长度** | **前缀** |
|-------------|-------------|----------------|----------------|--------|
| **P2PKH** | Base58Check | 25 字节 | 34 字符左右 | `1...` |
| **P2SH** | Base58Check | 25 字节 | 34 字符左右 | `3...` |
| **P2WPKH** | Bech32 | 21 字节 | 42~46 字符 | `bc1q...` |
| **P2TR** | Bech32m | 33 字节 | 58~62 字符 | `bc1p...` |
"""

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
import os
import hashlib
import base58


def generate_random_private_key():
    """生成随机私钥"""
    # 生成 32 字节的随机数据
    random_bytes = os.urandom(32)
    # 转换为十六进制
    private_key_hex = random_bytes.hex()
    return private_key_hex


def hex_to_wif(hex_key, testnet=True):
    """将十六进制私钥转换为 WIF 格式"""
    # 1. 添加版本号前缀 (0xEF 测试网, 0x80 主网)
    version = b'\xef' if testnet else b'\x80'

    # 2. 将十六进制转换为字节
    key_bytes = bytes.fromhex(hex_key)

    # 3. 添加版本号
    versioned_key = version + key_bytes

    # 4. 添加压缩标志
    with_compression = versioned_key + b'\x01'

    # 5. 计算双重 SHA256
    first_sha = hashlib.sha256(with_compression).digest()
    second_sha = hashlib.sha256(first_sha).digest()

    # 6. 取前4个字节作为校验和
    checksum = second_sha[:4]

    # 7. 组合最终结果
    final_key = with_compression + checksum

    # 8. Base58 编码
    wif = base58.b58encode(final_key).decode('utf-8')

    return wif


def main():
    # 设置测试网
    setup('testnet')

    # 生成随机私钥
    private_key_hex = generate_random_private_key()
    private_key_wif = hex_to_wif(private_key_hex)
    private_key = PrivateKey(private_key_wif)

    # 获取公钥
    public_key = private_key.get_public_key()

    print("\n=== 密钥信息 ===")
    print(f"私钥 (HEX): {private_key_hex}")
    print(f"私钥 (WIF): {private_key.to_wif()}")
    print(f"公钥 (HEX): {public_key.to_hex()}")

    print("\n=== 不同类型的地址 ===")
    # 获取传统地址 (P2PKH)
    legacy_address = public_key.get_address()
    print(f"传统地址: {legacy_address.to_string()}")

    # 获取 SegWit 地址 (P2WPKH)
    segwit_address = public_key.get_segwit_address()
    print(f"SegWit 地址: {segwit_address.to_string()}")

    # 获取 Taproot 地址 (P2TR)
    taproot_address = public_key.get_taproot_address()
    print(f"Taproot 地址: {taproot_address.to_string()}")

    print("\n=== 地址格式说明 ===")
    print("1. 传统地址 (P2PKH): 以 m 或 n 开头")
    print("2. SegWit 地址 (P2WPKH): 以 tb1q 开头")
    print("3. Taproot 地址 (P2TR): 以 tb1p 开头")

    print("\n=== 重要提示 ===")
    print("请务必保存好私钥信息！")

if __name__ == "__main__":
    main()
