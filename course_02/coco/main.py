from bitcoinlib.keys import Address
def segwit_to_legacy(segwit_address):
    """
    将 SegWit (bech32) 地址转换为 Legacy (P2PKH) 地址
    :param segwit_address: bc1q 开头的 SegWit 地址
    :return: 1 开头的 Legacy 地址
    """
    try:
        addr = Address.parse(segwit_address)
        legacy_address = addr.address(encoding='base58', script_type='p2pkh')
        return legacy_address
    except Exception as e:
        print(f"转换失败: {e}")
        return None

# 示例用法
segwit_addr = "bc1qx09txzh3hdpl458s24k496tj7qt7e8gwtweu8s"
legacy_addr = segwit_to_legacy(segwit_addr)
print(f"SegWit 地址: {segwit_addr}")
print(f"转换后的 Legacy 地址: {legacy_addr}")

def taproot_to_other(taproot_address):
    """
    将 Taproot 地址转换为 SegWit 和 Legacy 地址
    :param taproot_address: bc1p 开头的 Taproot 地址
    :return: 字典包含转换后的地址
    """
    try:
        addr = Address.parse(taproot_address)

        # 转换为 SegWit (P2WPKH)
        segwit_addr = addr.address(encoding='bech32', script_type='p2wpkh')

        # 转换为 Legacy (P2PKH)
        legacy_addr = addr.address(encoding='base58', script_type='p2pkh')

        return {
            'taproot': taproot_address,
            'segwit': segwit_addr,
            'legacy': legacy_addr
        }
    except Exception as e:
        print(f"转换失败: {e}")
        return None


# 示例用法
taproot_addr = "bc1p0emzc4px6agj9p7w0d9zpk7fgcu66837wz7rg52xy9q50d4t5y0svmpguc"
converted = taproot_to_other(taproot_addr)
print(f"原始 Taproot 地址: {converted['taproot']}")
print(f"转换后的 SegWit 地址: {converted['segwit']}")
print(f"转换后的 Legacy 地址: {converted['legacy']}")