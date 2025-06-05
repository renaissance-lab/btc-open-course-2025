# 02-reveal_keypath.py
# 使用 Alice 的私钥通过 Key Path 花费 Taproot 地址

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
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
    
    # 重建脚本（Key Path 花费需要完整的脚本树信息来计算 tweak）
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
    
    print(f"=== Alice Key Path 解锁 ===")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"Alice 私钥: {alice_private.to_wif()}")
    print(f"Alice 公钥: {alice_public.to_hex()}")
    print(f"花费方式: Key Path (最私密)")
    
    # 输入信息（需要替换为实际的 UTXO）
    commit_txid = "e0a56ac36bce3dfc094565285b4bc127497ef79b9b44720041b159b979158221"  # 替换为实际的交易ID
    input_amount = 187177  # 替换为实际金额
    output_amount = 2000  # 扣除手续费
    fee_amount = 200  # 扣除手续费
    reback_amount = input_amount - output_amount - fee_amount # 找零金额
    
    txout = TxOutput(output_amount, alice_public.get_taproot_address().to_script_pub_key())
    self_txout = TxOutput(reback_amount, taproot_address.to_script_pub_key()) #找零

    # 构建交易
    txin = TxInput(commit_txid, 0)
    tx = Transaction([txin], [txout, self_txout], has_segwit=True)
    
    print(f"\n=== 交易构建 ===")
    print(f"Input: {commit_txid}:0")
    print(f"Output: {alice_public.get_taproot_address().to_string()}")
    
    # Alice 使用 Key Path 签名
    # Key Path 需要完整的脚本树信息来计算正确的 tweak
    sig = alice_private.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],  # 输入的 scriptPubKey
        [input_amount],             # 输入金额
        script_path=False,                      # Key Path 花费
        tapleaf_scripts=tree                    # 完整的脚本树（用于计算 tweak）
    )
    
    print(f"Alice 签名: {sig}")
    
    # Key Path 花费的见证数据只包含签名
    tx.witnesses.append(TxWitnessInput([sig]))
    
    # 输出信息
    print(f"\n=== 交易信息 ===")
    print(f"Input Amount: {input_amount} satoshis")
    print(f"Output Amount: {output_amount} satoshis")
    print(f"Fee: {fee_amount} satoshis")
    print(f"TxId: {tx.get_txid()}")
    print(f"Raw Tx: {tx.serialize()}")
    
    print(f"\n=== Key Path 特性 ===")
    print("✅ 只需要 Alice 的私钥")
    print("✅ 见证数据只有一个签名，最小化")
    print("✅ 外界无法知道还有其他花费路径（完美隐私）")
    print("✅ 与普通的单签名交易无法区分")
    print("✅ 手续费最低，因为见证数据最少")
    
    print(f"\n=== 见证数据分析 ===")
    print("Key Path 见证数据结构:")
    print("  [alice_signature]  <- 只有一个元素")
    print("")
    print("对比 Script Path 见证数据结构:")
    print("  [signature/preimage, script, control_block]  <- 三个元素")
    print("")
    print("这就是 Key Path 的优势：简洁、私密、高效！")
    
    print(f"\n📝 使用说明:")
    print("1. 先运行 01-commit.py 创建地址并向其发送测试币")
    print("2. 替换 commit_txid 和 input_amount 为实际值")
    print("3. 运行此脚本进行 Key Path 花费")
    print("4. 只有 Alice 可以执行此花费")
    print("5. 这是最推荐的花费方式（如果 Alice 同意）")
    print("https://mempool.space/zh/testnet/tx/75b384d222192043409b8cf9ff50bf227e46d8c4a4f43746b943bbe8125523ff")

if __name__ == "__main__":
    main()