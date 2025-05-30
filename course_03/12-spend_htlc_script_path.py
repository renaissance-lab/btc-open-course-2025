"""
通过脚本路径花费 Taproot HTLC
参考官方示例：spend_p2tr_two_scripts_by_script_path.py

好的，让我详细描述这个场景：
场景假设:
1. Alice 想给 Bob 一笔钱，但有条件：
Bob 必须知道一个字符串 "helloworld" 才能获得这笔钱
如果 Bob 不知道这个字符串，就拿不到钱
代码执行过程:

# 1. Alice 创建 HTLC
preimage = "helloworld"  # 原像
preimage_hash = SHA256(preimage)  # = 936a185caaa266bb9cbe981e9e05cb78cd732b0b3280eb944412bb6f8f8f07af

# 2. Alice 创建锁定脚本
htlc_script = Script([
    'OP_SHA256',                # 对输入做 SHA256
    preimage_hash,              # 预期的哈希值
    'OP_EQUALVERIFY',          # 验证相等
    'OP_TRUE'                  # 如果相等就通过
])

# 3. Alice 创建 Taproot 地址并发送资金
from_address = internal_pub.get_taproot_address([[htlc_script]])
# 发送 0.00008000 BTC 到这个地址

# 4. Bob 使用 preimage 花费
tx.witnesses.append(TxWitnessInput([
    preimage_bytes.hex(),      # "helloworld" 的 hex
    htlc_script.to_hex(),      # 锁定脚本
    control_block.to_hex()     # Merkle 证明
]))
区块链浏览器解读:
交易: 01821ba7a0266ba39fde127a3c1713dc5dc37725fd9bfa7440a03fc2852d6649

输入:
- 金额: 0.00016059 tBTC
- 类型: V1_P2TR (Taproot)

见证数据 (Witness):
1. 68656c6c6f776f726c64 
   - 这是 "helloworld" 的 hex 编码
   - Bob 提供的原像

2. a820936a185caaa266bb9cbe981e9e05cb78cd732b0b3280eb944412bb6f8f8f07af8851
   - a8: OP_SHA256
   - 20: 32字节的 push
   - 936a...07af: 预期的哈希值
   - 88: OP_EQUALVERIFY
   - 51: OP_TRUE

3. c150be5f...6bb4d3
   - Control Block
   - 证明这个脚本确实在 Taproot 树中

输出:
- 地址: tb1pw44g2av8ctw92j3ahvmx54s48udtz2nvjtv5mlk87sgpn7luemfsdupt6e
- 金额: 0.00015859 tBTC

验证过程:
节点收到交易
看到 Taproot 脚本路径花费
执行脚本:
取 "helloworld"
计算 SHA256
与预期哈希值比较
匹配成功，交易有效
这就是为什么 Bob 只需要知道 "helloworld" 就能花费这笔钱，不需要任何私钥。
这种机制在闪电网络中很有用，因为它允许:
通过知识（preimage）而不是私钥来转移资金
原子性：要么 Bob 知道 preimage 并获得资金，要么完全无法获得
可验证：网络可以验证 Bob 确实知道 preimage

"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress
import hashlib

def main():
    # 设置测试网
    setup('testnet')
    
    # Alice 的密钥（内部密钥）
    internal_key = PrivateKey('')
    internal_pub = internal_key.get_public_key()
    
    # 创建 HTLC 脚本
    preimage = "helloworld"
    preimage_bytes = preimage.encode('utf-8')
    preimage_hash = hashlib.sha256(preimage_bytes).hexdigest()
    
    htlc_script = Script([
        'OP_SHA256',
        preimage_hash,
        'OP_EQUALVERIFY',
        'OP_TRUE'
    ])
    
    # 创建 Taproot 地址（与创建时使用相同的脚本）
    from_address = internal_pub.get_taproot_address([[htlc_script]])
    print("From Taproot address:", from_address.to_string())
    
    # 创建交易输入
    txin = TxInput(
        '47ec352a531c1ad21a465600e36f989aa0ccbefb36ed2b5037adcba7113e8df5',
        0
    )
    
    # 创建交易输出
    to_address = P2trAddress('tb1pw44g2av8ctw92j3ahvmx54s48udtz2nvjtv5mlk87sgpn7luemfsdupt6e')
    amount_to_send = 0.00015859
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )
    
    # 创建交易
    tx = Transaction([txin], [txout], has_segwit=True)
    
    # 输入金额和 scriptPubKey（用于签名）
    input_amount = 0.00008000
    amounts = [to_satoshis(input_amount)]
    scriptPubkey = from_address.to_script_pub_key()
    utxos_scriptPubkeys = [scriptPubkey]
    
    # 创建 control block
    control_block = ControlBlock(
        internal_pub,
        [htlc_script],  # 所有脚本叶子
        0,              # 当前脚本的索引
        is_odd=from_address.is_odd()
    )
    
    # 添加见证数据 [preimage, script, control_block]
    tx.witnesses.append(TxWitnessInput([
        preimage_bytes.hex(),
        htlc_script.to_hex(),
        control_block.to_hex()
    ]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已构造的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从地址: {from_address.to_string()}")
    print(f"到地址: {to_address.to_string()}")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {input_amount - amount_to_send} BTC")
    print("\nPreimage (hex):", preimage_bytes.hex())
    print("Script (hex):", htlc_script.to_hex())
    print("Control block:", control_block.to_hex())
    print("\nTxId:", tx.get_txid())
    print("Size:", tx.get_size())
    print("vSize:", tx.get_vsize())
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 