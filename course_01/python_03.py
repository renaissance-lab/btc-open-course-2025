# ===================================
# 文件：Python 和比特币类型示例代码
# 作者：Aaron Zhang
# 日期：2024年
# 说明：演示 Python 常用数据类型
#      以及比特币开发中的特殊类型
# ===================================
from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.script import Script
import hashlib
import json
from decimal import Decimal

def demo_bitcoin_types():
    # 设置比特币网络（测试网）
    setup('testnet')
    
    print("\n=== 1. 比特币地址和密钥 ===")
    # 私钥和公钥
    private_key = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    public_key = private_key.get_public_key()
    address = public_key.get_address()
    print(f"私钥 (WIF): {private_key.to_wif()}")
    print(f"公钥 (hex): {public_key.to_hex()}")
    print(f"地址: {address.to_string()}")

    print("\n=== 2. 哈希和十六进制 ===")
    # 字符串转十六进制
    text = "Hello, Bitcoin!"
    hex_text = text.encode('utf-8').hex()
    print(f"文本: {text}")
    print(f"十六进制: {hex_text}")
    
    # SHA256 哈希
    sha256_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    print(f"SHA256: {sha256_hash}")

    print("\n=== 3. 比特币金额 ===")
    # 使用 Decimal 处理比特币金额
    btc_amount = Decimal('0.00001234')
    satoshi_amount = int(btc_amount * Decimal('100000000'))
    print(f"BTC: {btc_amount}")
    print(f"聪: {satoshi_amount}")

    print("\n=== 4. JSON 处理 ===")
    # BRC-20 数据示例
    brc20_data = {
        "p": "brc-20",
        "op": "mint",
        "tick": "ordi",
        "amt": "1000"
    }
    json_str = json.dumps(brc20_data)
    print(f"JSON 字符串: {json_str}")
    # JSON 转回字典
    parsed_data = json.loads(json_str)
    print(f"解析后的数据: {parsed_data['tick']}")

    print("\n=== 5. 比特币脚本 ===")
    # 简单的脚本示例
    script = Script(['OP_1', 'OP_ADD', 'OP_2', 'OP_EQUAL'])
    print(f"脚本: {script.to_bytes()}")
    print(f"十六进制: {script.to_hex()}")

if __name__ == "__main__":
    demo_bitcoin_types()