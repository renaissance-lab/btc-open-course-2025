# 04-reveal_multisig.py
# 使用多签脚本路径花费 Taproot 地址

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

# 正确的Tapscript多签格式
# multisig_script = Script([
#     '0', # 初始计数器值为0
#     bob_public.to_x_only_hex(),
#     'OP_CHECKSIG',
#     carol_public.to_x_only_hex(),
#     'OP_CHECKSIGADD',
#     '2', # 需要2个签名
#     'OP_EQUAL'
# ])

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
    
    print(f"=== 多签脚本路径解锁 ===")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"使用脚本: {multisig_script} (索引 1)")
    print(f"需要 Bob 和 Carol 的签名")
    
    # 输入信息（需要替换为实际的 UTXO）
    commit_txid = "d541924aa4c66d5da7c4489385204ddca780944a0f021051498a680b63f54ee7"  # 替换为实际的交易ID
    input_amount = 0.00183277  # 替换为实际金额
    output_amount = 0.00001600  # 扣除手续费
    fee_amount = 0.00000250
    reback_amount = input_amount - output_amount- fee_amount
  
    txout = TxOutput(to_satoshis(output_amount), alice_public.get_taproot_address().to_script_pub_key())
    self_txout = TxOutput(to_satoshis(reback_amount), taproot_address.to_script_pub_key()) #找零
    # 构建交易
    txin = TxInput(commit_txid, 1)
    tx = Transaction([txin], [txout, self_txout], has_segwit=True)

    
    # 创建 Control Block
    # multisig_script 是索引 1
    control_block = ControlBlock(
        alice_public,           # internal_pub
        tree,                  # 脚本树
        1,                     # script_index (multisig_script 是第 1 个)
        is_odd=taproot_address.is_odd()
    )
    
    print(f"Control Block: {control_block.to_hex()}")
    
    # Bob 和 Carol 签名
    # 注意：多签脚本需要两个签名
    bob_sig = bob_private.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],
        [to_satoshis(input_amount)],
        script_path=True,
        tapleaf_script=multisig_script,
        tweak=False
    )
    
    carol_sig = carol_private.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],
        [to_satoshis(input_amount)],
        script_path=True,
        tapleaf_script=multisig_script,
        tweak=False
    )
    
    print(f"Bob 签名: {bob_sig}")
    print(f"Carol 签名: {carol_sig}")
    
    # 多签脚本路径花费
    # 见证数据格式：[bob_sig, carol_sig, script, control_block]
    # 注意：使用OP_CHECKSIGADD不再需要额外的空元素
    tx.witnesses.append(TxWitnessInput([
        bob_sig,                 # Bob 的签名
        carol_sig,               # Carol 的签名
        multisig_script.to_hex(), # 脚本的十六进制
        control_block.to_hex()    # 控制块的十六进制
    ]))
    
    # 输出信息
    print(f"\n=== 交易信息 ===")
    print(f"Input Amount: {input_amount} tBTC ({to_satoshis(input_amount)} satoshis)")
    print(f"Output Amount: {output_amount} tBTC ({to_satoshis(output_amount)} satoshis)")
    print(f"Fee: {input_amount - output_amount} tBTC ({to_satoshis(input_amount - output_amount)} satoshis)")
    print(f"TxId: {tx.get_txid()}")
    print(f"Raw Tx: {tx.serialize()}")
    
    print(f"\n=== 多签脚本路径特性 ===")
    print("✅ 需要 Bob 和 Carol 的签名")
    print("✅ 适合多方共同控制资金的场景")
    print("✅ 见证数据包含签名、脚本和控制块")
    print("✅ 比传统多签更私密，外界无法区分是否为多签")
    
    print(f"\n=== 见证数据分析 ===")
    print("多签脚本路径见证数据结构:")
    print("  [bob_sig, carol_sig, script_hex, control_block_hex]  <- 四个元素")
    print("")
    print("对比 Key Path 见证数据结构:")
    print("  [alice_signature]  <- 只有一个元素")
    print("")
    print("多签脚本路径的优势：多方共同控制，更安全！")
    
    print(f"\n📝 使用说明:")
    print("1. 先运行 01-commit.py 创建地址并向其发送测试币")
    print("2. 替换 commit_txid 和 input_amount 为实际值")
    print("3. 运行此脚本进行多签脚本路径花费")
    print("4. 需要 Bob 和 Carol 的私钥")

if __name__ == "__main__":
    main()