r'''
比特币钱包生成器 - 自己手搓拼接

本程序用于创建比特币测试网钱包，生成私钥、公钥、地址和WIF格式,通过本例介绍一些基础知识。

输出示例:
===== 比特币测试网钱包 =====
地址: mtcUJ4H94D4VhWE3n8VSVEFG4V2K1qVRja
私钥(HEX): 2d4cc82c6ab7b2feb8e7268a69373492e4087cd8783d43d93064a7c6658bfbea
私钥(WIF): cP6kxoT6rau6x1Ljku55Vb2xFA9ox5ZC8Eg1kexdpaSzKM8A673z
公钥(压缩),字节: b'\x03\xbc\xa5\x95\xc2\xad\xc2`d\xe5\x1aUK\xc5\x0b\x01\x87%\xeb\x9a\x8c`\xc6/\x93\x7f\xae\xc0\xae\xf2\x96\x98\n'
公钥(压缩): 03bca595c2adc26064e51a554bc50b018725eb9a8c60c62f937faec0aef296980a
公钥(未压缩): 04bca595c2adc26064e51a554bc50b018725eb9a8c60c62f937faec0aef296980a9d5436348fb62abf83bc5344e963595ecef26f7f927178bed7ffa37f39339311

以下为详细概念解释：

0. 地址: mtcUJ4H94D4VhWE3n8VSVEFG4V2K1qVRja
   - 这是一个P2PKH(Pay to Public Key Hash)类型的比特币测试网地址
   - 地址以"m"开头，表明这是测试网地址(由前缀0x6F确定)
   - 34个字符长度，包含了Base58编码后的[前缀+公钥哈希+校验和]

1. 私钥(HEX): 3f94562ff2c85f1f2e4193f1bc9d85a157d90a84849c51ff64f45e029c704b28
   - 这是一个随机生成的32字节(256位)的数字，用十六进制表示为64个字符
   - 私钥是钱包的核心，控制着钱包中所有资产的所有权
   - 在代码中通过random.randint(0, 255)生成32个随机字节

2. 私钥(WIF): 924vDQQ5xunCSbhe29DtDjQY3BYZnqFdfT1R4hyawnLzXkUu9a8
   - WIF(Wallet Import Format)是私钥的用户友好表示形式
   - 生成过程:
     a. 添加前缀字节0xEF(十进制239)，表示这是测试网私钥
     b. 计算双重SHA256哈希，取前4字节作为校验和
     c. 将[前缀+私钥+校验和]通过Base58编码得到WIF字符串
   - 总共37字节(1前缀+32私钥+4校验和)，经Base58编码变为51-52个字符
   - 使用WIF可以在大多数钱包软件中轻松导入私钥

3. 公钥(未压缩): 04ae8ad65d446813d3745934ddab5f176c64d671a3e2db91e3b17f7e8644f21a936c04b7db839f8caad551be4dddd0b12cc42bb4bcbcbd2663f2efab6237519c59
   - 通过SECP256k1椭圆曲线加密算法从私钥派生出的公钥
   - 相比压缩格式，多存储了Y坐标信息
   - 未压缩格式: 65字节(130个十六进制字符)
     a. 1字节前缀0x04，表示未压缩公钥
     b. 32字节X坐标: ae8ad65d446813d3745934ddab5f176c64d671a3e2db91e3b17f7e8644f21a93
     c. 32字节Y坐标: 6c04b7db839f8caad551be4dddd0b12cc42bb4bcbcbd2663f2efab6237519c59

4. 公钥(压缩): 03ae8ad65d446813d3745934ddab5f176c64d671a3e2db91e3b17f7e8644f21a93
   - 压缩格式: 33字节(66个十六进制字符)
     a. 1字节前缀(0x02或0x03)，表示Y坐标的奇偶性
       - 0x02: Y坐标为偶数
       - 0x03: Y坐标为奇数(本例中使用0x03，表示Y坐标为奇数)
     b. 32字节X坐标
   - 压缩公钥可以节省空间，特别是在区块链上存储交易时
   - 这是推荐在区块链上使用的格式，节省空间和手续费

5. 公钥(压缩),字节: b'\x03\xbc\xa5\x95\xc2\xad\xc2`d\xe5\x1aUK\xc5\x0b\x01\x87%\xeb\x9a\x8c`\xc6/\x93\x7f\xae\xc0\xae\xf2\x96\x98\n'
   - 这是Python的bytes对象表示法，显示了33字节的压缩公钥
   - \xNN格式表示不可打印或特殊的字节(十六进制表示)
   - 可打印ASCII字符直接显示为字符本身
   - \x03前缀表示Y坐标为奇数

6. 地址: mhEMAY2yKRCWfM3ppcRrJe2pkZSzuVGQ7k
   - 这是一个P2PKH(Pay to Public Key Hash)类型的比特币测试网地址
   - 生成过程:
     a. 对公钥进行SHA-256哈希
     b. 对结果进行RIPEMD-160哈希，得到20字节的公钥哈希(PUBKEY HASH)
     c. 添加测试网前缀0x6F
     d. 计算双重SHA-256校验和，取前4字节
     e. 将[前缀+公钥哈希+校验和]通过Base58编码
   - 总共25字节(1前缀+20公钥哈希+4校验和)，Base58编码后得到约34个字符
   - 地址以"m"开头，这是因为测试网前缀0x6F在Base58编码后通常会生成"m"或"n"开头的字符串
   - 与之对应，主网前缀0x00会生成"1"开头的地址

安全注意事项:
1. 私钥是唯一可以控制比特币的密钥，必须安全保存
2. 任何获得私钥的人都可以控制相应地址中的所有资金
3. 测试网地址只能用于测试网络，不能用于真实比特币交易
4. 哈希函数和椭圆曲线加密保证了从公钥无法反推私钥，从地址无法反推公钥

比特币地址类型，主要是生成 4 种比特币地址：
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


公钥数据格式比较:
1. 字节对象表示: 原始二进制数据在Python中的显示方式，将一些字节显示为转义序列(\x)
2. 十六进制表示: 每个字节转换为两位十六进制数，连接成字符串，统一且易读

压缩与未压缩公钥:
- 压缩公钥只存储X坐标和Y坐标的奇偶性(通过前缀03或02表示)
- 未压缩公钥存储完整的X和Y坐标
- 两种格式可以互相转换，因为椭圆曲线方程可以从X坐标计算出Y坐标(有两个解，通过前缀区分)
- 压缩格式生成的地址与未压缩格式生成的地址不同
   
交易流程:
使用私钥签名交易，通过公钥验证签名有效性，向目标地址转账。
整个过程是: 私钥生成公钥，公钥生成地址，私钥用于签名交易，公钥用于验证签名。

本程序生成的是测试网P2PKH地址，可以在测试网区块浏览器查看:
https://live.blockcypher.com/btc-testnet/address/mhEMAY2yKRCWfM3ppcRrJe2pkZSzuVGQ7k/
'''
import hashlib
import base58
import ecdsa
import binascii
import random

class BitcoinTestNetWallet:
    def __init__(self):
        # 测试网版本前缀
        self.TESTNET_PRIVATE_KEY_PREFIX = b'\xef'  # 测试网私钥前缀
        self.TESTNET_ADDRESS_PREFIX = b'\x6f'      # 测试网地址前缀
    
    def generate_private_key(self):
        """生成一个随机的私钥"""
        # 生成32字节（256位）的随机数作为私钥
        private_key_bytes = bytes([random.randint(0, 255) for _ in range(32)])
        return private_key_bytes
    
    def private_key_to_wif(self, private_key_bytes):
        """将私钥转换为WIF格式"""
        # 添加前缀
        extended_key = self.TESTNET_PRIVATE_KEY_PREFIX + private_key_bytes
        
        # 计算校验和
        first_sha = hashlib.sha256(extended_key).digest()
        second_sha = hashlib.sha256(first_sha).digest()
        checksum = second_sha[:4]
        
        # 拼接并编码
        wif_key_bytes = extended_key + checksum
        wif_key = base58.b58encode(wif_key_bytes).decode('utf-8')
        
        return wif_key
    
    def get_public_key(self, private_key_bytes):
        """从私钥生成公钥"""
        # 使用SECP256k1曲线
        sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        
        # 获取公钥并添加前缀0x04
        public_key = b'\x04' + vk.to_string()
        
        # 压缩公钥版本
        x_coord = vk.to_string()[:32]
        y_coord = vk.to_string()[32:]
        if int.from_bytes(y_coord, byteorder='big') % 2 == 0:
            compressed_public_key = b'\x02' + x_coord
        else:
            compressed_public_key = b'\x03' + x_coord
        
        return {
            'uncompressed': public_key.hex(),
            'compressed': compressed_public_key.hex()
        }
    
    def public_key_to_address(self, public_key_hex):
        """从公钥生成比特币地址"""
        # 将公钥转换为字节
        public_key_bytes = bytes.fromhex(public_key_hex)
        
        # 计算SHA-256哈希
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        
        # 计算RIPEMD-160哈希
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        ripemd160_hash = ripemd160.digest()
        
        # 添加测试网前缀
        prefixed_ripemd160_hash = self.TESTNET_ADDRESS_PREFIX + ripemd160_hash
        
        # 计算校验和
        first_sha = hashlib.sha256(prefixed_ripemd160_hash).digest()
        second_sha = hashlib.sha256(first_sha).digest()
        checksum = second_sha[:4]
        
        # 拼接并编码
        address_bytes = prefixed_ripemd160_hash + checksum
        address = base58.b58encode(address_bytes).decode('utf-8')
        
        return address
    
    def generate_wallet(self):
        """生成一个完整的钱包，包括私钥、公钥、地址和WIF"""
        # 生成私钥
        private_key_bytes = self.generate_private_key()
        private_key_hex = private_key_bytes.hex()
        
        # 转换为WIF格式
        wif = self.private_key_to_wif(private_key_bytes)
        
        # 获取公钥
        public_keys = self.get_public_key(private_key_bytes)
        
        # 从压缩公钥生成地址
        address = self.public_key_to_address(public_keys['compressed'])
        
        return {
            'private_key': private_key_hex,
            'wif': wif,
            'public_key': public_keys,
            'address': address
        }

if __name__ == "__main__":
    wallet = BitcoinTestNetWallet()
    wallet_data = wallet.generate_wallet()
    
    print("\n===== 比特币测试网钱包,使用自己手搓拼接 =====")
    print(f"地址: {wallet_data['address']}")
    print()
    print(f"私钥(HEX): {wallet_data['private_key']}")
    print(f"私钥(WIF): {wallet_data['wif']}")
    print(f"公钥(未压缩): {wallet_data['public_key']['uncompressed']}")
    print(f"公钥(压缩): {wallet_data['public_key']['compressed']}")
    print("\n重要提示：")
    print("1. 请保存好私钥和WIF，这是访问钱包的唯一方式")
    print("2. 这是测试网地址，只能在测试网络使用")
    print(f"3. 可以在测试网浏览器查看该地址：https://mempool.space/testnet/address/{wallet_data['address']}/")
