
"""
P2SH有两个验证阶段：
第一阶段 - 脚本哈希验证：
Previous output script: OP_HASH160 [20字节哈希] OP_EQUAL
ScriptSig: [签名] [完整的redeem script]

验证过程：
1. 取出ScriptSig中的最后一个元素(redeem script)
2. 计算其HASH160
3. 与输出脚本中的哈希比较
4. 如果匹配，进入第二阶段
第二阶段 - Redeem Script执行：
执行栈：[签名] + [公钥 OP_CHECKSIG]
1. 压入签名到栈
2. 压入公钥到栈
3. 执行OP_CHECKSIG验证签名
2. P2SH的优势
对发送方：

只需要知道收款地址，无需了解复杂的解锁条件
交易大小固定，手续费可预测

对接收方：

可以创建复杂的解锁条件（多重签名、时间锁等）
隐私性更好，解锁条件直到花费时才公开

对网络：

减少区块链存储压力
复杂脚本的存储成本由使用者承担

3. 代码中的关键点
python# 创建redeem script (这是实际的解锁逻辑)
redeem_script = Script([p2pk_pk, "OP_CHECKSIG"])

# 生成P2SH地址 (基于redeem script的哈希)
p2sh_addr = P2shAddress.from_script(redeem_script)

# 签名时使用redeem script而不是输出脚本
sig = p2pk_sk.sign_input(tx, 0, redeem_script)

# 解锁脚本包含签名和完整的redeem script
txin.script_sig = Script([sig, redeem_script.to_hex()])
4. P2SH vs P2PKH对比
特性P2PKHP2SH地址格式1xxx或mxxx3xxx或2xxx解锁复杂度简单(签名+公钥)灵活(任意脚本)隐私性公钥哈希可见脚本内容隐藏手续费负担发送方接收方
"""


from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, PrivateKey, P2shAddress
from bitcoinutils.script import Script


def main():
    # always remember to setup the network
    setup("testnet")

    #
    # This script spends from a P2SH address containing a P2PK script
    #

    # create transaction input from tx id of UTXO (contained 0.1 tBTC)
    txin = TxInput(
        "35f53eec504b0f025d489574e4e063ddcb80cc5066024a16d55cc84462e79678", 0
    )

    # secret key needed to spend P2PK that is wrapped by P2SH
    p2pk_sk = PrivateKey("cRvyLwCPLU88jsyj94L7iJjQX5C2f8koG4G2gevN4BeSGcEvfKe9")
    p2pk_pk = p2pk_sk.get_public_key().to_hex()
    # create the redeem script - needed to sign the transaction
    redeem_script = Script([p2pk_pk, "OP_CHECKSIG"])

    # 打印 P2SH 地址
    p2sh_addr = P2shAddress.from_script(redeem_script)
    print("\nfrom address,P2SH 地址为:", p2sh_addr.to_string())

    to_addr = P2pkhAddress("mqDTgsqYoy5vRdNVRnJBcup6gBndGfg529")
    print("\nto address,P2PKH 地址为:", to_addr.to_string())
    txout = TxOutput(to_satoshis(0.00001600), to_addr.to_script_pub_key())

    # no change address - the remaining 0.01 tBTC will go to miners)

    # create transaction from inputs/outputs -- default locktime is used
    tx = Transaction([txin], [txout])
    
    # print raw transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # use the private key corresponding to the address that contains the
    # UTXO we are trying to spend to create the signature for the txin -
    # note that the redeem script is passed to replace the scriptSig
    sig = p2pk_sk.sign_input(tx, 0, redeem_script)
    # print(sig)

    # set the scriptSig (unlocking script)
    txin.script_sig = Script([sig, redeem_script.to_hex()])
    signed_tx = tx.serialize()

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + signed_tx)
    print("\nTxId:", tx.get_txid())


if __name__ == "__main__":
    main()
