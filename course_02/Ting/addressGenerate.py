from bitcoinutils.keys import PrivateKey
from bitcoinutils.setup import setup
# 生成legacy、segwit和taproot地址
def generate_addresses(private_key,network = 'testnet'):
    setup(network)

    public_key = private_key.get_public_key()
    print("公钥: ", public_key.to_hex())

    # 生成legacy地址s
    legacy_address = public_key.get_address('p2pkh').to_string()
    legacy_address1 = public_key.get_address() # 同样可以
    # print("legacy地址: ", legacy_address.to_string())
    # print("legacy地址2: ", legacy_address1.to_string())
    
    # 生成segwit地址
    segwit_address = public_key.get_segwit_address().to_string()
    
    # print("segwit地址: ", segwit_address.to_string())

    # # 生成taproot地址
    taproot_address = public_key.get_taproot_address().to_string()
    
    return {
        'legacy': legacy_address,
        'segwit': segwit_address,
        'taproot': taproot_address
    }



if __name__ == "__main__":
    # 生成一个新的随机私钥
    priv = PrivateKey()

    # 获取私钥的WIF格式
    print("私钥（WIF）: ", priv.to_wif())

    address = generate_addresses(priv,)
    print('legacy地址：',address['legacy'])
    print('segwit地址：',address['segwit'])
    print('Taproot地址：',address['taproot'])


