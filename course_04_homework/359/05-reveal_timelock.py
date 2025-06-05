# 05-reveal_timelock.py
# 使用时间锁定脚本路径花费 Taproot 地址

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
import hashlib

def main():
    setup('testnet')
    
    # Alice 的密钥（内部密钥）
    alice_private = PrivateKey('cNqNeGWmf8MsMiuRi3qJj7okPBZvH3J2iEkC42sMcPYjmzCzdTCS')
    alice_public = alice_private.get_public_key()
    
    # Bob 和 Carol 的密钥，用于多签脚本
    bob_private = PrivateKey('cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6')
    bob_public = bob_private.get_public_key()
    
    carol_private = PrivateKey('cTeSvY5tq6CmPXcrr9puFsxgd3tHH2P5uoW3SYcMLVFBGhY2qExY')
    carol_public = carol_private.get_public_key()
    
    # 重建脚本
    # Script 1: 哈希锁
    preimage = "secretword"
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    hashlock_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])

    # Script 2: 多签脚本
    multisig_script = Script([
        'OP_2', # 需要2个签名
        bob_public.to_x_only_hex(),
        carol_public.to_x_only_hex(),
        'OP_2', # 共2个公钥
        'OP_CHECKMULTISIG'
    ])

    # Script 3: 时间锁定脚本
    timelock_script = Script([
        100, # 100个区块的相对时间锁
        'OP_CHECKSEQUENCEVERIFY',
        'OP_DROP',
        'OP_TRUE'
    ])
    
    # 重建脚本树
    tree = [[hashlock_script, multisig_script], timelock_script]
    taproot_address = alice_public.get_taproot_address(tree)
    
    print(f"=== 时间锁定脚本路径解锁 ===")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"使用脚本: {timelock_script} (索引 2)")
    print(f"需要等待100个区块后才能花费")
    

    
    # 输入信息（需要替换为实际的 UTXO）
    commit_txid = "d541924aa4c66d5da7c4489385204ddca780944a0f021051498a680b63f54ee7"  # 替换为实际的交易ID
    input_amount = 183277  # 替换为实际金额（satoshis）
    output_amount = 1600  # 输出金额（satoshis）
    fee_amount = 250  # 手续费（satoshis）
    reback_amount = input_amount - output_amount - fee_amount  # 找零金额（satoshis）
  
    txout = TxOutput(output_amount, alice_public.get_taproot_address().to_script_pub_key())
    self_txout = TxOutput(reback_amount, taproot_address.to_script_pub_key()) #找零
    # 构建交易
    # sequence 值必须大于等于脚本中指定的值（这里是100）
    # 将整数100转换为字节序列
    sequence_bytes = (100).to_bytes(4, byteorder='little')
    txin = TxInput(commit_txid, 1, sequence=sequence_bytes)
    tx = Transaction([txin], [txout, self_txout], has_segwit=True)

    
    # 创建 Control Block
    # timelock_script 是索引 2
    control_block = ControlBlock(
        alice_public,           # internal_pub
        tree,                  # 脚本树
        2,                     # script_index (timelock_script 是第 2 个)
        is_odd=taproot_address.is_odd()
    )
    
    # 将Control Block保存到变量中，避免多次打印
    control_block_hex = control_block.to_hex()
    print(f"Control Block: {control_block_hex}")
    
    # 时间锁定脚本路径花费
    # 见证数据格式：[script, control_block]
    # 注意：时间锁定脚本不需要签名，只需要满足时间条件
    tx.witnesses.append(TxWitnessInput([
        timelock_script.to_hex(), # 脚本的十六进制
        control_block_hex         # 控制块的十六进制
    ]))
    
    # 输出信息
    print(f"\n=== 交易信息 ===")
    print(f"Input Amount: {input_amount} satoshis")
    print(f"Output Amount: {output_amount} satoshis")
    print(f"Fee: {fee_amount} satoshis")
    print(f"Tx: {tx}")
    print(f"TxId: {tx.get_txid()}")
    print(f"Raw Tx: {tx.serialize()}")
    
    print(f"\n=== 时间锁定脚本路径特性 ===")
    print("✅ 不需要私钥，只需要等待足够的时间")
    print("✅ 交易的 sequence 值必须大于等于脚本中指定的值")
    print("✅ 适合托管、遗产规划等场景")
    print("✅ 见证数据包含脚本和控制块")
    
    print(f"\n=== 见证数据分析 ===")
    print("时间锁定脚本路径见证数据结构:")
    print("  [script_hex, control_block_hex]  <- 两个元素")
    print("")
    print("对比 Key Path 见证数据结构:")
    print("  [alice_signature]  <- 只有一个元素")
    print("")
    print("时间锁定脚本路径的优势：无需私钥，只需等待时间！")
    
    print(f"\n⚠️ 重要提示 ⚠️")
    print("1. 这个交易只有在满足时间条件后才能被网络接受")
    print("2. 对于 OP_CHECKSEQUENCEVERIFY，交易的 sequence 值必须大于等于脚本中指定的值")
    print("3. 相对时间锁是相对于 UTXO 被确认的区块高度计算的")
    print("4. 如果交易被拒绝，可能是因为时间条件尚未满足")
    
    print(f"\n📝 使用说明:")
    print("1. 先运行 01-commit.py 创建地址并向其发送测试币")
    print("2. 替换 commit_txid 和 input_amount 为实际值")
    print("3. 等待至少100个区块后运行此脚本")
    print("4. 不需要任何私钥，只需要满足时间条件")

if __name__ == "__main__":
    main()