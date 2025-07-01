"""
BitcoinLib 地址生成器（支持 P2PKH 和 P2WPKH）
=========================================

【说明】
使用 bitcoinlib 生成 Legacy 和 SegWit 地址。
GitHub Issue #263 明确表示 python-bitcoinlib 不支持 Taproot，这是个从2021年10月开放至今的功能请求
Taproot 地址由于库的限制需要其他解决方案。

【限制】
- bitcoinlib (0.7.x) 对 Taproot 支持有限
- Taproot 需要密钥调整和 bech32m 编码
- 推荐使用 bitcoinutils/btclib 或其他库生成 Taproot 地址

"""

from bitcoinlib.keys import Key, Address
from bitcoinlib.scripts import Script
import json

def generate_bitcoin_addresses(network='testnet'):
    """
    生成比特币地址（P2PKH 和 P2WPKH）
    
    Args:
        network: 'bitcoin' 或 'testnet'
    
    Returns:
        dict: 包含私钥和地址信息
    """
    # 生成密钥
    key = Key(network=network)
    
    print("\n===== 产生一个比特币测试网新钱包,使用bitcoinlib库 =====")
    
    # 私钥信息
    print("\n【私钥信息】")
    print(f"HEX: {key.private_hex}")
    print(f"WIF: {key.wif()}")
    print(f"十进制: {key.secret}")
    
    # 公钥信息
    print("\n【公钥信息】")
    print(f"压缩: {key.public_hex}")
    print(f"未压缩: {key.public_uncompressed_hex}")
    print(f"X坐标: {hex(key.x)}")
    print(f"Y坐标: {hex(key.y)}")
    
    # 生成地址
    print("\n【生成的地址】")
    
    # 1. P2PKH (Legacy)
    legacy_address = key.address()
    print(f"\n1. P2PKH (Legacy):")
    print(f"   地址: {legacy_address}")
    if network == 'testnet':
        expected = legacy_address[0] in ['m', 'n']
        print(f"   前缀: {legacy_address[0]} ({'✓ 正确' if expected else '✗ 错误'})")
    else:
        expected = legacy_address[0] == '1'
        print(f"   前缀: {legacy_address[0]} ({'✓ 正确' if expected else '✗ 错误'})")
    
    # 2. P2WPKH (Native SegWit)
    segwit_address = None
    print(f"\n2. P2WPKH (Native SegWit):")
    
    try:
        # 方法1: 使用 Address 类
        addr_obj = Address(
            hashed_data=key.public_key_hash(),
            prefix=network,
            script_type='p2wpkh',
            encoding='bech32',
            witness_type='segwit'
        )
        segwit_address = str(addr_obj)
    except Exception as e1:
        try:
            # 方法2: 尝试 address() 方法的参数
            segwit_address = key.address(script_type='p2wpkh', encoding='bech32')
        except Exception as e2:
            print(f"   生成失败: {e2}")
    
    if segwit_address:
        print(f"   地址: {segwit_address}")
        if network == 'testnet':
            expected = segwit_address.startswith('tb1q')
            print(f"   前缀: {segwit_address[:4]} ({'✓ 正确' if expected else '✗ 错误'})")
        else:
            expected = segwit_address.startswith('bc1q')
            print(f"   前缀: {segwit_address[:4]} ({'✓ 正确' if expected else '✗ 错误'})")
    
    # 3. P2TR (Taproot) - 说明限制
    print(f"\n3. P2TR (Taproot):")
    print(f"   状态: 不支持")
    print(f"   原因: bitcoinlib 缺少完整的 Taproot 实现")
    print(f"   说明: Taproot 需要:")
    print(f"        - 密钥调整 (key tweaking)")
    print(f"        - bech32m 编码 (而非 bech32)")
    print(f"        - x-only 公钥 (32字节)")
    print(f"   建议: 使用 buidl-python 或其他支持库")
    

    
    # 返回结果
    return {
        'network': network,
        'private_key': {
            'hex': key.private_hex,
            'wif': key.wif(),
            'decimal': str(key.secret)
        },
        'public_key': {
            'compressed': key.public_hex,
            'uncompressed': key.public_uncompressed_hex,
            'x': hex(key.x),
            'y': hex(key.y)
        },
        'addresses': {
            'p2pkh': legacy_address,
            'p2wpkh': segwit_address,
            'p2tr': 'not_supported'
        }
    }

def demonstrate_taproot_issue():
    """
    演示 Taproot 地址生成的问题
    """
    
    print("\n=====Taproot 地址生成问题演示=====")
    
    
    # 使用bitcoinlib论坛中的示例私钥
    private_key_wif = 'KxVSwjuqNb6qe3KTLsHG5nYA3WFEqrjyKnGbwgHAreiWsqrwffuh'
    k = Key(private_key_wif)
    
    print(f"\n私钥 (WIF): {private_key_wif}")
    print(f"公钥 (压缩): {k.public_hex}")
    
    # 尝试生成 Taproot 地址
    print("\n尝试生成 Taproot 地址:")
    
    try:
        # 方法1: 使用 Address 类
        taproot_addr = Address(
            data=k.public_hex,
            prefix='bc',
            script_type='p2tr',
            encoding='bech32',
            witness_type='taproot',
            witver=1,
            network='bitcoin'
        )
        print(f"生成的地址: {taproot_addr}")
        print("注意: 这个地址可能不正确，因为缺少密钥调整")
    except Exception as e:
        print(f"生成失败: {e}")
    
    print("\n正确的 Taproot 地址应该是: bc1pfkde37d8chuqa6tgwvp7rwmtl7vvd20ql6g5433xxpdah30t7nushrsrlu")
    print("差异原因: bitcoinlib 没有实现 Taproot 的密钥调整算法")



def main():
    """主函数"""
    # 生成地址
    testnet_result = generate_bitcoin_addresses('testnet')
    
    # 演示 Taproot 问题
    demonstrate_taproot_issue()
    

if __name__ == "__main__":
    main()