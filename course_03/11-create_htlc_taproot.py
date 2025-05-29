"""
创建一个带有哈希时间锁的 Taproot 地址

两种花费方式：
1. 密钥路径：Alice 可以直接用私钥花费
2. 脚本路径：任何人可以通过提供 preimage "helloworld" 来花费

注意：这个地址将用于接收资金，之后可以通过两种方式之一花费

=== HTLC Taproot 地址信息 ===
Alice 公钥: 0250be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d3
Preimage: helloworld
Preimage Hash: 936a185caaa266bb9cbe981e9e05cb78cd732b0b3280eb944412bb6f8f8f07af
Taproot 地址: tb1p53ncq9ytax924ps66z6al3wfhy6a29w8h6xfu27xem06t98zkmvsakd43h

脚本路径信息:
Script: ['OP_SHA256', '936a185caaa266bb9cbe981e9e05cb78cd732b0b3280eb944412bb6f8f8f07af', 'OP_EQUALVERIFY', 'OP_TRUE']

使用说明:
1. 向这个 Taproot 地址发送比特币
2. 可以通过以下方式花费:
   - Alice 使用她的私钥（密钥路径）
   - 任何人提供正确的 preimage 'helloworld'（脚本路径）
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
    
    # Alice 的密钥
    alice_private = PrivateKey('')
    alice_public = alice_private.get_public_key()
    
    # 创建 preimage 的哈希
    preimage = "helloworld"
    preimage_bytes = preimage.encode('utf-8')
    preimage_hash = hashlib.sha256(preimage_bytes).hexdigest()
    
    # 创建脚本路径 - 验证 preimage
    tr_script = Script([
        'OP_SHA256',
        preimage_hash,
        'OP_EQUALVERIFY',
        'OP_TRUE'
    ])
    
    # 创建 Taproot 地址（结合密钥路径和脚本路径）
    taproot_address = alice_public.get_taproot_address([[tr_script]])
    
    print("\n=== HTLC Taproot 地址信息 ===")
    print(f"Alice 私钥: {alice_private.to_wif()}")
    print(f"Alice 公钥: {alice_public.to_hex()}")
    print(f"Preimage: {preimage}")
    print(f"Preimage Hash: {preimage_hash}")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    
    print("\n脚本路径信息:")
    print(f"Script: {tr_script}")
    
    print("\n使用说明:")
    print("1. 向这个 Taproot 地址发送比特币")
    print("2. 可以通过以下方式花费:")
    print("   - Alice 使用她的私钥（密钥路径）")
    print("   - 任何人提供正确的 preimage 'helloworld'（脚本路径）")

if __name__ == "__main__":
    main() 