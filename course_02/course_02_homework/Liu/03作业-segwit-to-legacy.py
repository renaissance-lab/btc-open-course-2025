import requests
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress
from bitcoinutils.script import Script

# 设置为测试网
setup('testnet')

# 私钥和公钥（示例，使用你的私钥）
private_key_wif = "cW6Apppb5wbMfTyEa8BV4NNUPguxWdaymdQ8nGKhcEqRaWnkcLEt"
priv = PrivateKey(private_key_wif)
pub = priv.get_public_key()

# 从 SegWit 地址（P2WPKH）发送
from_address = pub.get_segwit_address()

# 接收方 P2PKH 地址
to_address = "msMAeRZrgJVGEXpSi4cXHtA4Dok7MyQoEU"

# UTXO 信息（假设你从一个具体的 UTXO 提供了数据）
utxo_txid = "1679a532d5e64d6cb71c334b792f97c7d0ce546e694179f39cb2bf2033cb4058"
utxo_vout = 1

# 发送金额
amount_to_send = 0.00040829  # 发送金额（比特币）


script_code = Script(
        ["OP_DUP", "OP_HASH160", pub.to_hash160(), "OP_EQUALVERIFY", "OP_CHECKSIG"]
)

# 创建交易输入（从 SegWit UTXO）
tx_in = TxInput(utxo_txid, utxo_vout)

# 交易输出（发送到 P2PKH 地址）
to_addr = P2pkhAddress(to_address)
tx_out = TxOutput(to_satoshis(amount_to_send), to_addr.to_script_pub_key())

# 构建交易对象
tx = Transaction([tx_in], [tx_out],has_segwit=True)

# 使用私钥对输入进行 SegWit 签名
sig = priv.sign_segwit_input(tx, 0, script_code, to_satoshis(0.00041829))
pk = priv.get_public_key().to_hex()

# 使用 TxWitnessInput 设置见证数据（SegWit 签名数据）
tx.witnesses.append(TxWitnessInput([sig, pk]))

# 序列化交易（获取原始交易的十六进制表示）
signed_tx = tx.serialize()
print(f"签名后的交易（十六进制）:\n{signed_tx}")

# 广播交易
print("\n广播交易...")
mempool_api = "https://mempool.space/testnet/api/tx"
try:
    response = requests.post(mempool_api, data=signed_tx)
    if response.status_code == 200:
        txid = response.text
        print(f"交易成功！")
        print(f"交易ID: {txid}")
        print(f"查看交易: https://mempool.space/testnet/tx/{txid}")
    else:
        print(f"广播失败: {response.text}")
except Exception as e:
    print(f"错误: {e}")
