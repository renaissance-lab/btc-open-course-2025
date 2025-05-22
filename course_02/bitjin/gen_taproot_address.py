from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey

# 设置为 testnet 或 mainnet
setup('testnet')

# 生成一个私钥（你也可以从 WIF 导入）
priv = PrivateKey()

# 获取公钥对象
pub = priv.get_public_key()

# 生成 Taproot 地址（P2TR）
taproot_address = pub.get_taproot_address()

# 输出
print("私钥（WIF）:", priv.to_wif())
print("Taproot 地址（P2TR）:", taproot_address.to_string())


# 私钥（WIF）: cSqDDxiKf5PbFoVTLZmYeuM73AE84tuofLvjRi7SnSW5F7571MK9
# Taproot 地址（P2TR）: tb1puvylqtuqq6lmffnhs0ych986z5qrp4pnyah40zsayu4qq5js6azq6ltz4l