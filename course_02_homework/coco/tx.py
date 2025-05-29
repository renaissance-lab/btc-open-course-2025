from bitcoinlib.wallets import Wallet, wallet_delete_if_exists
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import HDKey
import json

# 删除已存在的钱包（仅用于演示）

# 1. 创建一个包含三种地址类型的钱包
passphrase = Mnemonic().generate()
print(f"助记词: {passphrase}")

w = Wallet.create('mywallet', keys=passphrase, network='bitcoin')

# 派生三种地址
legacy_key = w.new_key(script_type='p2pkh')  # Legacy
segwit_key = w.new_key(script_type='p2wpkh')  # SegWit
taproot_key = w.new_key(script_type='p2tr')  # Taproot

print(f"Legacy地址: {legacy_key.address}")
print(f"SegWit地址: {segwit_key.address}")
print(f"Taproot地址: {taproot_key.address}")

# 2. 模拟UTXO（实际应用中从区块链获取）
# 注意：实际使用时需要替换为真实的UTXO数据
utxos = [
    {  # Legacy UTXO
        'address': legacy_key.address,
        'txid': 'aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899',
        'output_n': 0,
        'value': 100000,  # 0.001 BTC
        'script': legacy_key.script,
        'script_type': 'p2pkh'
    },
    {  # SegWit UTXO
        'address': segwit_key.address,
        'txid': '112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00',
        'output_n': 1,
        'value': 150000,  # 0.0015 BTC
        'script': segwit_key.script,
        'script_type': 'p2wpkh'
    },
    {  # Taproot UTXO
        'address': taproot_key.address,
        'txid': '00112233445566778899aabbccddeeff112233445566778899aabbccddeeff11',
        'output_n': 0,
        'value': 200000,  # 0.002 BTC
        'script': taproot_key.script,
        'script_type': 'p2tr'
    }
]

# 3. 创建交易
output_address = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'  # 中本聪地址作为示例输出

# 计算总输入金额
total_input = sum(u['value'] for u in utxos)
print(f"总输入金额: {total_input} satoshis ({total_input / 1e8} BTC)")

# 估算手续费（根据输入类型和数量）
# 假设: Legacy输入=110vB, SegWit=68vB, Taproot=58vB
fee_rate = 20  # sat/vB (当前网络费率)
estimated_vsize = 110 + 68 + 58 + 31  # 输入 + 1个输出(31vB)
estimated_fee = fee_rate * estimated_vsize
print(f"预估手续费: {estimated_fee} satoshis ({estimated_fee / 1e8} BTC)")

# 计算输出金额
output_amount = total_input - estimated_fee
print(f"输出金额: {output_amount} satoshis ({output_amount / 1e8} BTC)")

# 构建交易
t = Transaction(network='bitcoin')

# 添加输入
for utxo in utxos:
    t.add_input(
        prev_txid=utxo['txid'],
        output_n=utxo['output_n'],
        value=utxo['value'],
        script=utxo['script'],
        script_type=utxo['script_type']
    )

# 添加输出
t.add_output(output_amount, output_address)

# 4. 签名交易（每种输入类型需要不同的签名方式）
for i, utxo in enumerate(utxos):
    key = None
    if utxo['script_type'] == 'p2pkh':
        key = legacy_key
    elif utxo['script_type'] == 'p2wpkh':
        key = segwit_key
    elif utxo['script_type'] == 'p2tr':
        key = taproot_key

    if key:
        # 获取私钥用于签名
        private_key = HDKey(key.key_private)

        # 根据输入类型签名
        if utxo['script_type'] == 'p2pkh':
            t.sign(key=private_key, index=i, hash_type='SIGHASH_ALL')
        elif utxo['script_type'] == 'p2wpkh':
            t.sign(key=private_key, index=i, hash_type='SIGHASH_ALL')
        elif utxo['script_type'] == 'p2tr':
            t.sign(key=private_key, index=i, hash_type='SIGHASH_DEFAULT')

# 5. 验证和输出交易
if t.verify():
    print("\n交易验证成功!")
    print(f"原始交易: {t.raw_hex()}")
    print("\n交易详情:")
    print(json.dumps(t.as_dict(), indent=4))
else:
    print("交易验证失败!")