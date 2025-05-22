"""
比特币不同类型地址比较

观察legacy、segwit和taproot地址的长短，以及它们的锁定脚本(scriptpubkey)的区别。
"""

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script

def main():
    # 设置测试网
    setup('testnet')
    
    # 生成私钥
    private_key = PrivateKey.from_wif('cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6')
    public_key = private_key.get_public_key()
    
    # 生成不同类型的地址
    legacy_address = public_key.get_address()
    segwit_address = public_key.get_segwit_address()
    taproot_address = public_key.get_taproot_address()
    
    print("\n=== 不同类型的地址比较 ===\n")
    
    # 打印地址
    print(f"Legacy地址: {legacy_address.to_string()}")
    print(f"Legacy地址长度: {len(legacy_address.to_string())}字符")
    
    print(f"\nSegWit地址: {segwit_address.to_string()}")
    print(f"SegWit地址长度: {len(segwit_address.to_string())}字符")
    
    print(f"\nTaproot地址: {taproot_address.to_string()}")
    print(f"Taproot地址长度: {len(taproot_address.to_string())}字符")
    
    print("\n=== 地址格式说明 ===\n")
    print("1. Legacy地址 (P2PKH): 以 m 或 n 开头 (测试网)")
    print("2. SegWit地址 (P2WPKH): 以 tb1q 开头 (测试网)")
    print("3. Taproot地址 (P2TR): 以 tb1p 开头 (测试网)")
    
    print("\n=== 锁定脚本(scriptpubkey)比较 ===\n")
    
    # 获取并打印锁定脚本
    legacy_script = legacy_address.to_script_pub_key()
    segwit_script = segwit_address.to_script_pub_key()
    taproot_script = taproot_address.to_script_pub_key()
    
    print(f"Legacy锁定脚本: {legacy_script}")
    print(f"Legacy锁定脚本长度: {len(str(legacy_script))}字符")
    print(f"Legacy锁定脚本操作码数量: {len(legacy_script.script)}")
    
    print(f"\nSegWit锁定脚本: {segwit_script}")
    print(f"SegWit锁定脚本长度: {len(str(segwit_script))}字符")
    print(f"SegWit锁定脚本操作码数量: {len(segwit_script.script)}")
    
    print(f"\nTaproot锁定脚本: {taproot_script}")
    print(f"Taproot锁定脚本长度: {len(str(taproot_script))}字符")
    print(f"Taproot锁定脚本操作码数量: {len(taproot_script.script)}")
    
    print("\n=== 锁定脚本结构分析 ===\n")
    print("Legacy (P2PKH): OP_DUP OP_HASH160 <PubKeyHash> OP_EQUALVERIFY OP_CHECKSIG")
    print("SegWit (P2WPKH): OP_0 <PubKeyHash>")
    print("Taproot (P2TR): OP_1 <32字节公钥>")
    
    print("\n=== 地址和锁定脚本的区别 ===\n")
    print("1. Legacy地址最短，但锁定脚本最长，需要5个操作码")
    print("2. SegWit地址比Legacy长，但锁定脚本更短，只需要2个操作码")
    print("3. Taproot地址最长，锁定脚本与SegWit类似，也是2个操作码，但使用了不同的版本号和更长的公钥")

if __name__ == "__main__":
    main()