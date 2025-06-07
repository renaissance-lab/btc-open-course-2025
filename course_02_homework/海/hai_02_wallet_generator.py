import os
from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import setup
from bit import Key
from bitcoinlib.keys import Address

'''
后续测试使用的私钥和地址：

私钥（WIF） Segwit: cVgbLBMymtebKVGoriSVWxEBahbGvvx3tuKJftGpaJBcfjujZd4C
公钥（HEX): 02791c756a773e606ab0e05dbdb453dec465d0796b94ceb536a2fa19ddca9efef4

 === 不同类型地址1 ===
Legacy地址: n4juXXS637FKJy9zJsbrCbTLvdQLRZCjST
Segwit地址: tb1ql67l67sy6zn6d2ztf75chu3h498ydupplwscpt
Taproot地址: tb1phsw7yj630jtay3c5vmf3mkv7kdja5889m0lmjz0h0ks8xusk03usj0xlnp

--------------------------------------------

私钥（WIF） Taproot: cMhdj1dKsv7EftcmLPZtwAvWwFCW8uLLHY136smwCbRBNXouuRxC
公钥（HEX): 027b8f70283619aef70ef1d76605531e31af8cd0effcac4651e9dc7f49cd656339

 === 不同类型地址2 ===
Segwit地址: tb1q7aum99m2j40x3gq9s056sepzjrs84py3ccnwsd
Taproot地址: tb1p484vwajatgstnx82fssqtprljpj9g3ruzj9h8hx03sjnggjcpxesjzzjpg
'''

# 生成一个随机的私钥
def generate_random_private_key():
    
    # 生成32个随机字节
    random_bytes = os.urandom(32)

    # 将随机字节转换为整数，并创建私钥
    private_key = PrivateKey(secret_exponent=int.from_bytes(random_bytes, byteorder="big")) 

    # 返回私钥
    return private_key

def valid_address(address):
    try:
        addr_type = Address.parse(address)
        print(f"✅ 地址有效 | 类型: {addr_type}")
    except Exception as e:
        print(f"❌ 地址无效: {e}")

def generate_three_address(private_key):
    # 获取公钥
    public_key = private_key.get_public_key()
    print(f"公钥（HEX): {public_key.to_hex()}")

    print(f"\n === 不同类型地址 === ")
    # 获取Legacy地址
    legacy_address = public_key.get_address()
    print(f"Legacy地址: {legacy_address.to_string()}")

    # 获取Segwit地址
    segwit_address = public_key.get_segwit_address()
    print(f"Segwit地址: {segwit_address.to_string()}")

    # 获取Taproot地址
    taproot_address = public_key.get_taproot_address()
    print(f"Taproot地址: {taproot_address.to_string()}")

if __name__ == '__main__':
    # 设置为测试网络
    setup('testnet')
    # 生成一个随机的私钥
    private_key = generate_random_private_key()
    print(f"私钥（WIF）: {private_key.to_wif()}")
    
    # 生成三个地址
    generate_three_address(private_key)