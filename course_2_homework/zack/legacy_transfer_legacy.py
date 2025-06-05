"""
最简单的比特币测试网转账示例
从一个P2PKH地址转账到另一个P2PKH地址

可以反复用的两个地址分别是（也可以使用最新的地址）：
私钥 (WIF格式): cTnhHT1VVnvf7fAgDtVXAxbYdBC6BujGs4D1qN9P9oJm2UtKkBo7
地址: n14GXhPZ4GWMmojsZr53LfHVNxCekQBaSH

私钥 (WIF格式): cQbmoSHZ9jWnfyBoY82ZqZht9taid82beJtAYpRcwKaDSxizd37a
地址: msmkSKovoadUpdjbKMiancy6PnKowe4VP1

重点解释锁定脚本
to_addr.to_script_pub_key()
OP_DUP OP_HASH160 <接收方的hash160> OP_EQUALVERIFY OP_CHECKSIG
发送的时候发送的是锁定脚本

解锁用的脚本是<签名><公钥>
sig = sk.sign_input(tx, 0, previous_locking_script)
pk = sk.get_public_key().to_hex()
unlocking_script= Script([sig, pk])
tx_in.script_sig = unlocking_script

本例还直接进行了广播
"""

import requests
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, PrivateKey
from bitcoinutils.script import Script

# 设置为测试网
setup('testnet')

# 转账参数
private_key_wif = "cQdaT7vwbLipdTbniB6BvUUBqSz6TFz23weiMB3iUveLyGiEVpx1"
from_address = "msZcKAKkLfy3E8t3PKrQmDz7tUpkLKE41e"
to_address = "mm46s3okAgjMrTWkFQnwchNNea39E4CmQw"

# UTXO信息（从你提供的浏览器数据）
utxo_txid = "33ed4b585fdd0be7ef5d46bbbd22341ecaca45ca447cf65865da6be68a615a53"
utxo_vout = 0
utxo_value = 1000  # 当前余额：1000聪

# 转账金额和手续费
amount = 700  # 发送800聪
fee = 300      # 手续费200聪

# 1. 创建交易输入（从UTXO）
tx_in = TxInput(utxo_txid, utxo_vout)

# 2. 创建交易输出（给接收方）
to_addr = P2pkhAddress(to_address)
tx_out = TxOutput(amount, to_addr.to_script_pub_key())

# 3. 构建交易
tx = Transaction([tx_in], [tx_out])

# 4. 对交易签名
sk = PrivateKey(private_key_wif)
from_addr = P2pkhAddress(from_address)

# 创建锁定脚本（对于P2PKH地址）
# 创建锁定脚本还有更简单办法就是 直接使用 to_script_pub_key() 方法
previous_locking_script = from_addr.to_script_pub_key()
# ['OP_DUP', 'OP_HASH160', '866dd9cc8a6953d0f4f489f70d642fc3fa084af8', 'OP_EQUALVERIFY', 'OP_CHECKSIG']
# previous_locking_script = Script([
#     "OP_DUP",
#     "OP_HASH160", 
#     from_addr.to_hash160(),
#     "OP_EQUALVERIFY",
#     "OP_CHECKSIG"
# ])

print(previous_locking_script)
# exit()


# 签名并设置解锁脚本
sig = sk.sign_input(tx, 0, previous_locking_script)
pk = sk.get_public_key().to_hex()
unlocking_script= Script([sig, pk])
tx_in.script_sig = unlocking_script

# 5. 序列化交易（获取原始交易十六进制）
signed_tx = tx.serialize()
print(f"签名后的交易（十六进制）:\n{signed_tx}")

# 6. 广播交易
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
    
# https://mempool.space/testnet/tx/6f14be3c9cb12cc04abf5707d82fe8c0fc6a43e11a55acf526e47f44f756ea84