from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress, P2trAddress, PublicKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from mnemonic import Mnemonic
from hdwallet import HDWallet
from hdwallet.symbols import BTC, BTCTEST
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Optional
import os
import hashlib
import base58

def compare_address_lengths():
    """比较不同类型比特币地址的长度和特点"""
    # 设置为测试网
    setup('testnet')
    
    # 创建随机私钥
    private_key = PrivateKey()
    public_key = private_key.get_public_key()
    
    # 生成不同类型的地址
    legacy_addr = public_key.get_address().to_string()
    segwit_addr = public_key.get_segwit_address().to_string()
    taproot_addr = public_key.get_taproot_address().to_string()
    
    # 打印地址及其长度进行比较
    print("\n=== 地址长度比较 ===")
    print(f"Legacy 地址: {legacy_addr}")
    print(f"长度: {len(legacy_addr)} 字符")
    print(f"前缀: {legacy_addr[0]} (测试网为m或n开头，主网为1开头)")
    
    print(f"\nSegWit 地址: {segwit_addr}")
    print(f"长度: {len(segwit_addr)} 字符")
    print(f"前缀: {segwit_addr[:4]} (测试网为tb1q开头，主网为bc1q开头)")
    
    print(f"\nTaproot 地址: {taproot_addr}")
    print(f"长度: {len(taproot_addr)} 字符")
    print(f"前缀: {taproot_addr[:4]} (测试网为tb1p开头，主网为bc1p开头)")
    
    # 地址区别总结
    print("\n=== 地址区别总结 ===")
    print("1. Legacy地址(P2PKH): 使用Base58编码，较短，兼容性最好")
    print("2. SegWit地址(P2WPKH): 使用Bech32编码，中等长度，交易费用更低")
    print("3. Taproot地址(P2TR): 使用Bech32m编码，最长，提供更好的隐私性和扩展性")
    
    return private_key, public_key, legacy_addr, segwit_addr, taproot_addr

def compare_scriptpubkey():
    """比较不同类型比特币地址的锁定脚本(scriptpubkey)"""
    # 设置为测试网
    setup('testnet')
    
    # 创建随机私钥和公钥
    private_key = PrivateKey()
    public_key = private_key.get_public_key()
    
    # 生成不同类型的地址对象
    legacy_addr_obj = public_key.get_address()
    segwit_addr_obj = public_key.get_segwit_address()
    taproot_addr_obj = public_key.get_taproot_address()
    
    # 获取各地址类型的锁定脚本
    legacy_script = legacy_addr_obj.to_script_pub_key()
    segwit_script = segwit_addr_obj.to_script_pub_key()
    taproot_script = taproot_addr_obj.to_script_pub_key()
    
    # 打印各锁定脚本及其长度
    print("\n=== 锁定脚本(ScriptPubKey)比较 ===")
    
    print(f"\nLegacy ScriptPubKey: {legacy_script.to_hex()}")
    print(f"脚本内容: {legacy_script}")
    print(f"长度: {len(legacy_script.to_hex())//2} 字节")
    
    print(f"\nSegWit ScriptPubKey: {segwit_script.to_hex()}")
    print(f"脚本内容: {segwit_script}")
    print(f"长度: {len(segwit_script.to_hex())//2} 字节")
    
    print(f"\nTaproot ScriptPubKey: {taproot_script.to_hex()}")
    print(f"脚本内容: {taproot_script}")
    print(f"长度: {len(taproot_script.to_hex())//2} 字节")
    
    # 脚本区别总结
    print("\n=== 锁定脚本区别总结 ===")
    print("1. Legacy(P2PKH): OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG")
    print("   - 最复杂的脚本，需要进行更多操作")
    
    print("2. SegWit(P2WPKH): OP_0 <witnessProgramHash>")
    print("   - 更简短的脚本，将签名数据移至见证数据中")
    
    print("3. Taproot(P2TR): OP_1 <32-byte output key>")
    print("   - 最短的脚本，使用Schnorr签名，支持更复杂的支出条件")
    
    return legacy_script, segwit_script, taproot_script

def segwit_to_legacy(segwit_address):
    """从SegWit地址生成对应的Legacy地址
    
    Args:
        segwit_address: 一个SegWit地址字符串(tb1q开头)
        
    Returns:
        对应的Legacy地址(P2PKH)
    """
    # 设置测试网
    setup('testnet')
    
    # 对于这个示例，我们需要一个有私钥的地址来演示转换
    # 创建一个新的私钥
    private_key = PrivateKey()
    public_key = private_key.get_public_key()
    
    # 生成SegWit地址
    segwit_addr_obj = public_key.get_segwit_address()
    segwit_addr = segwit_addr_obj.to_string()
    
    # 生成对应的Legacy地址
    legacy_addr = public_key.get_address().to_string()
    
    print(f"\n新生成的SegWit地址: {segwit_addr}")
    print(f"转换为Legacy地址: {legacy_addr}")
    print(f"注意: 此转换需要使用原始公钥生成两种地址，而不是直接从一个地址转到另一个地址")
    
    # 现在解释如何手动转换，如果我们知道原始公钥
    print("\n转换原理:")
    print("1. SegWit地址(P2WPKH)是公钥哈希的bech32编码")
    print("2. Legacy地址(P2PKH)是同样公钥哈希的base58编码")
    print("3. 两者使用相同的公钥哈希，但编码和脚本类型不同")
    
    # 如果我们不知道原始公钥，则无法准确转换
    # 但对于给定的segwit_address参数，我们可以演示它的结构
    print(f"\n对于提供的SegWit地址: {segwit_address}")
    print("无法直接转换为Legacy地址，因为我们不知道原始公钥")
    
    return legacy_addr

def taproot_to_segwit_and_legacy(taproot_address, private_key_wif=None):
    """从Taproot地址生成对应的SegWit和Legacy地址
    
    注意：因为Taproot使用不同的公钥方案，直接转换需要原始私钥或公钥
    
    Args:
        taproot_address: 一个Taproot地址字符串(tb1p开头)
        private_key_wif: 可选的私钥WIF字符串(如果有)
        
    Returns:
        (segwit_address, legacy_address)元组
    """
    # 设置测试网
    setup('testnet')
    
    # 如果有私钥，我们可以直接从私钥生成所有地址
    if private_key_wif:
        try:
            private_key = PrivateKey(private_key_wif)
            public_key = private_key.get_public_key()
            
            # 生成SegWit和Legacy地址
            segwit_addr = public_key.get_segwit_address().to_string()
            legacy_addr = public_key.get_address().to_string()
            
            print(f"\n从原始私钥生成三种地址:")
            print(f"Taproot地址: {public_key.get_taproot_address().to_string()}")
            print(f"SegWit地址: {segwit_addr}")
            print(f"Legacy地址: {legacy_addr}")
            
            return segwit_addr, legacy_addr
        except Exception as e:
            print(f"\n使用提供的私钥生成地址时出错: {str(e)}")
    
    # 如果没有提供私钥或者出错，使用新私钥进行演示
    print("\n注意：从Taproot地址直接转换到其他类型需要原始私钥")
    print("这是因为Taproot使用Schnorr签名和不同的公钥转换方式")
    print("而SegWit和Legacy地址使用ECDSA签名和不同的公钥处理方式")
    print("\n关于Taproot地址概念:")
    print("1. Taproot地址使用x-only公钥（32字节）")
    print("2. 其使用Schnorr签名替代ECDSA")
    print("3. 使用bech32m编码（改进版bech32）")
    
    # 演示使用新私钥生成三种地址
    print("\n演示使用新私钥生成三种地址:")
    private_key = PrivateKey()
    public_key = private_key.get_public_key()
    
    new_taproot_addr = public_key.get_taproot_address().to_string()
    new_segwit_addr = public_key.get_segwit_address().to_string()
    new_legacy_addr = public_key.get_address().to_string()
    
    print(f"私钥(WIF): {private_key.to_wif()}")
    print(f"Taproot地址: {new_taproot_addr}")
    print(f"SegWit地址: {new_segwit_addr}")
    print(f"Legacy地址: {new_legacy_addr}")
    
    # 对于给定的taproot_address，说明无法直接转换
    print(f"\n对于提供的Taproot地址: {taproot_address}")
    print("无法直接转换为SegWit或Legacy地址，除非使用原始私钥")
    
    return new_segwit_addr, new_legacy_addr

def mnemonic_demo():
    """展示从助记词生成不同类型的地址"""
    # 生成助记词
    # mnemonic: str = generate_mnemonic(language="english", strength=128)
    mnemonic = "impact mouse twenty guide rate airport differ easy limb door gold axis"
    print(f"助记词: {mnemonic}")
    
    # 生成 HDWallet
    hdwallet: HDWallet = HDWallet(symbol=BTCTEST)
    hdwallet.from_mnemonic(mnemonic=mnemonic)
    
    # 1. 传统地址 (P2PKH) - BIP44
    path = "m/44'/1'/0'/0/0"
    hdwallet.from_path(path)
    print(f"\n传统地址 (BIP44 - {path}): {hdwallet.p2pkh_address()}")
    print(f"=== 密钥信息 ({path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()
    
    # 2. SegWit兼容地址 (P2SH-P2WPKH) - BIP49
    path = "m/49'/1'/0'/0/0"
    hdwallet.from_path(path)
    print(f"\nSegWit兼容地址 (BIP49 - {path}): {hdwallet.p2sh_address()}")
    print(f"=== 密钥信息 ({path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()
    
    # 3. 原生SegWit地址 (P2WPKH) - BIP84
    path = "m/84'/1'/0'/0/0"
    hdwallet.from_path(path)
    print(f"\n原生SegWit地址 (BIP84 - {path}): {hdwallet.p2wpkh_address()}")
    print(f"=== 密钥信息 ({path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()
    
    # 4. Taproot地址 (P2TR) - BIP86
    # 注意：hdwallet库可能不支持p2tr_address方法，具体取决于版本
    # 这里使用bitcoinutils库生成taproot地址
    setup('testnet')
    private_key = PrivateKey(hdwallet.wif())
    public_key = private_key.get_public_key()
    taproot_addr = public_key.get_taproot_address().to_string()
    
    path = "m/86'/1'/0'/0/0"  # Taproot路径
    print(f"\nTaproot地址 (BIP86 - {path}): {taproot_addr}")
    print(f"=== 密钥信息 ({path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()

def main():
    # 设置为测试网
    setup('testnet')
    
    # 比较不同类型比特币地址的长度和特点
    print("\n===== 1. 比较不同类型比特币地址的长度和特点 =====")
    private_key, public_key, legacy_addr, segwit_addr, taproot_addr = compare_address_lengths()
    
    # 比较不同类型比特币地址的锁定脚本
    print("\n===== 2. 比较不同类型比特币地址的锁定脚本 =====")
    compare_scriptpubkey()
    
    # 从SegWit地址生成Legacy地址
    print("\n===== 3. 从SegWit地址生成Legacy地址 =====")
    segwit_to_legacy(segwit_addr)
    
    # 从Taproot地址生成SegWit和Legacy地址
    print("\n===== 4. 从Taproot地址生成SegWit和Legacy地址 =====")
    taproot_to_segwit_and_legacy(taproot_addr, private_key.to_wif())
    
    # 显示助记词生成的地址演示
    print("\n===== 5. 助记词生成地址演示 =====")
    mnemonic_demo()
    
if __name__ == "__main__":
    main()
    
    
    
    