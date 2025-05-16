"""
使用 bitcoinlib 创建 Legacy 到 Legacy 的测试网交易
结合这个例子，介绍utxo的使用
bitcoinlib对发送交易做了封装，进行配置就可以

关键要点：
1. 必须在 Transaction 构造函数中指定 witness_type='legacy'，否则可能生成 SegWit 格式
2. 确保交易格式正确：
   - Legacy 交易以 '01000000' 开头
3. 手续费要满足最低要求（测试网通常要求至少 1 sat/byte）

常见错误及解决方案：
- "TX decode failed"：交易包含 SegWit 标记，确保 witness_type='legacy'
- "bad-txns-inputs-missingorspent"：检查 UTXO 是否存在且未被花费
- "min relay fee not met"：增加手续费（对于 ~192 字节的交易，至少需要 192 sats）
- 广播失败：确保在正确的网络广播（测试网地址在测试网广播）

调试技巧：
- 检查交易开头是否为 '01000000'
- 检查是否包含 witness flag '0001'
- 验证交易 t.verify()

本例进行手动广播，在tools文件夹下有广播的工具，或者演示浏览器广播
"""
from bitcoinlib.transactions import Transaction, Input, Output
from bitcoinlib.keys import Key


# 创建密钥
ki = Key('cQbmoSHZ9jWnfyBoY82ZqZht9taid82beJtAYpRcwKaDSxizd37a', network='testnet')
print(f"Address: {ki.address()}")

# 创建输入
transaction_input = Input(
    prev_txid='b9365d43fc7a63dd56481e4b51b22632302dfdd1a23cea95cb25bc18d473d507',
    output_n=0,
    keys=ki.public(),
    network='testnet'
)

# 创建输出
transaction_output = Output(
    value=1000,
    address='mkDeKvM5BwXHt4SDLxE5kjwDiNtc8UUzmC',
    network='testnet',
    witness_type='legacy',  # 明确指定 legacy
    script_type='p2pkh'     # 明确指定 p2pkh
)

# 创建交易
t = Transaction([transaction_input], [transaction_output], network='testnet', witness_type='legacy')

# 签名
t.sign(ki.private_byte)

# 输出结果
print(f"\nRaw transaction: {t.raw_hex()}")
print(f"Verified: {t.verify()}")

# 验证是否是纯 legacy 格式
raw_hex = t.raw_hex()
if raw_hex[:8] == '01000000' and '0001' not in raw_hex[:12]:
    print("\n✓ Transaction is pure legacy format!")
    print(f"Size: {len(raw_hex)//2} bytes")
    print(f"\nYou can broadcast this transaction hex:")
    print(raw_hex)
else:
    print("\n✗ Transaction format issue detected")