from bitcoinutils.mnemonics import Mnemonic
from bitcoinutils.keys import HDKey
from bitcoinutils.constants import TESTNET  # 使用 Testnet

def create_testnet_wallet():
    # 1. 生成随机助记词 (BIP39)
    mnemonic = Mnemonic()
    words = mnemonic.generate()
    print("助记词 (Mnemonic):", words)

    # 2. 从助记词生成种子 (BIP39)
    seed = mnemonic.to_seed(words)

    # 3. 生成主私钥 (BIP32 Root Key)
    root_key = HDKey.from_seed(seed, TESTNET)  # 使用 TESTNET

    # 4. 按 BIP44 路径派生 Testnet 私钥 (m/44'/1'/0'/0/0)
    #    - 44' : BIP44 标准
    #    - 1'  : Testnet 的 coin_type (主网是 0')
    #    - 0'  : 账户索引
    #    - 0   : 外部链 (收款地址)
    #    - 0   : 地址索引
    path = "m/44'/1'/0'/0/0"
    child_key = root_key.derive(path)

    # 5. 获取 WIF 格式的私钥
    private_key_wif = child_key.to_wif(compressed=True)
    print("私钥 (WIF):", private_key_wif)

    # 6. 获取 Testnet 地址 (P2PKH 格式，如 'm...' 或 'n...')
    address = child_key.get_address()
    print("Testnet 地址:", address.to_string())

    return {
        "mnemonic": words,
        "private_key": private_key_wif,
        "address": address.to_string()
    }

# 执行
wallet = create_testnet_wallet()