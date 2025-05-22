from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2wpkhAddress, P2pkhAddress, P2trAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.script import Script
from bitcoinlib.encoding import to_bytes
import requests

# 用于生成地址
def generate_address():
    # 设置网络为testnet
    setup('testnet')

    private_key_wif = "cQbmoSHZ9jWnfyBoY82ZqZht9taid82beJtAYpRcwKaDSxizd37a"
    private_key = PrivateKey(private_key_wif)

    # 生成公钥
    public_key = private_key.get_public_key()

    print("\n === 密钥信息 ===")
    print(f"私钥（WIF): {private_key.to_wif()}")
    print(f"公钥（HEX): {public_key.to_hex()}")

    print("\n === 不同类型的地址 ===")

    # 获取传统legacy地址
    legacy_address = public_key.get_address()
    print(f"传统Legacy地址: {legacy_address.to_string()}")

    # 获取SegWit地址
    segwit_address = public_key.get_segwit_address()
    print(f"SegWit地址: {segwit_address.to_string()}")

    #获取Taproot地址
    taproot_address = public_key.get_taproot_address()
    print(f"Taproot地址: {taproot_address.to_string()}")

    return legacy_address, segwit_address, taproot_address

# 从segwit地址到legacy地址的转账
def segwit_to_legacy_transaction():
    setup('testnet')

    # 发送方信息
    from_private_key = PrivateKey("cQbmoSHZ9jWnfyBoY82ZqZht9taid82beJtAYpRcwKaDSxizd37a")
    from_pub = from_private_key.get_public_key()

    # 获取脚本代码
    script_code = from_pub.get_address().to_script_pub_key()

    from_segwit_address = P2wpkhAddress('tb1q840vrzv5lfuj5m6udgc3p75m0uk888w0daves5')
    to_legacy_address = P2pkhAddress('mzCyg57PeU6KfJ1rxzcQ6BEgJaemosj8pU')

    print(f"\n === segwit到legacy地址的转账 ===")

    print(f"\n发送方 SegWit地址：{from_segwit_address.to_string()}")
    print(f"接收方 Legacy地址：{to_legacy_address.to_string()}")

    # 构建交易输入
    txin = TxInput('bb13224a3b8771f5a2637053b07c6e1e028db0a26b3cc4ccb96ebb7eb750ae4b',
                   0)

    amount_send = 800
    fee = 200
    total_input = amount_send + fee
    print(f"\n输入金额：{total_input} satoshi")

    txout = TxOutput(amount_send, to_legacy_address.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    print("\n 未签名的交易：")
    print(tx.serialize())

    sig = from_private_key.sign_segwit_input(tx,
                                             0,
                                             script_code,
                                             total_input)
    
    txin.script_sig = Script([])
    public_key = from_private_key.get_public_key().to_hex()
    tx.witnesses.append(TxWitnessInput([sig, public_key]))

    signed_tx = tx.serialize()

    print("\n 已签名的交易:")
    print(signed_tx)

# Taproot地址到Segwit地址的转账
def taproot_to_segwit():
    setup('testnet')

    # 发送方信息
    from_private_key = PrivateKey("cQbmoSHZ9jWnfyBoY82ZqZht9taid82beJtAYpRcwKaDSxizd37a")
    from_pub = from_private_key.get_public_key()

    # 获取脚本代码
    script_code = from_pub.get_address().to_script_pub_key()

    from_taproot_address = P2trAddress('tb1pqc89pwzzaxlk2vsx9pxpshwzp9ce7rvyxur3esdl3tjwur65f4vstu0svc')
    to_segwit_address = P2wpkhAddress('tb1q840vrzv5lfuj5m6udgc3p75m0uk888w0daves5')

    print(f"\n === taproot到taproot地址的转账 ===")

    print(f"\n发送方 taproot地址：{from_taproot_address.to_string()}")
    print(f"接收方 segwit地址：{to_segwit_address.to_string()}")

    # 构建交易输入
    txin = TxInput('bb13224a3b8771f5a2637053b07c6e1e028db0a26b3cc4ccb96ebb7eb750ae4b',
                   0)

    amount_send = 800
    fee = 200
    total_input = amount_send + fee
    print(f"\n输入金额：{total_input} satoshi")

    txout = TxOutput(amount_send, to_segwit_address.to_script_pub_key())

    tx = Transaction([txin], [txout], has_segwit=True)

    print("\n 未签名的交易：")
    print(tx.serialize())

    sig = from_private_key.sign_taproot_input(tx,
                                             0,
                                             [script_code],
                                             [total_input])
    
    txin.script_sig = Script([])
    public_key = from_private_key.get_public_key().to_hex()
    tx.witnesses.append(TxWitnessInput([sig, public_key]))

    signed_tx = tx.serialize()

    print("\n 已签名的交易:")
    print(signed_tx)

if __name__ == "__main__":
    print(f"/n === 根据 私钥生成三种地址 ===")
    generate_address()

    print(f"/n === 从segwit地址到legacy地址的转账 ===")
    segwit_to_legacy_transaction()

    print(f"/n === Taproot地址到Segwit和Legacy地址的转账 ===")
    taproot_to_segwit()