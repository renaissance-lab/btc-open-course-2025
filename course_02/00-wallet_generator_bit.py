'''
比特币钱包生成器 (bit库实现) - 技术 
核心特性：
1. 密码学操作：
   - 自动处理所有密码学原语
   - 安全的私钥随机数生成
   - 符合 BIP32/BIP39/BIP44 标准规范

2. 库的优势：
   - 封装复杂的密码学操作
   - 返回字节对象（需要.hex()转换为十六进制）
   - 完整的交易签名和广播功能
'''

from bit import Key, PrivateKeyTestnet

def generate_wallet():
    # 主网钱包生成
    key = Key()
    
    # 测试网钱包生成
    testnet_key = PrivateKeyTestnet()
    
    # 打印钱包信息
    print("\n===== 产生一个比特币测试网新钱包,使用bit python库 =====")
    print(f"地址: {testnet_key.address}")
    print()
    print(f"私钥(HEX): {testnet_key.to_hex()}")
    print(f"私钥(WIF): {testnet_key.to_wif()}")
    print(f"公钥(压缩),字节: {testnet_key.public_key}")
    print(f"公钥(压缩): {testnet_key.public_key.hex()}")
    print(f"公钥(未压缩): {testnet_key._pk.public_key.format(compressed=False).hex()}")
    
    print("\n重要提示：")
    print("1. 请保存好私钥和WIF，这是访问钱包的唯一方式")
    print("2. 这是测试网地址，只能在测试网络使用")
    print(f"3. 可以在测试网浏览器查看该地址：https://mempool.space/testnet/address/{testnet_key.address}/")

if __name__ == "__main__":
    generate_wallet()