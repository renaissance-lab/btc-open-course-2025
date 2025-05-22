# segwit 到 taproot 地址的转账代码
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
# from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2wpkhAddress, PrivateKey, P2pkhAddress, P2trAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息
    from_private_key = PrivateKey('cMqjK1H7Jgt3m6K6bBCyv387GwB6yq9iwRHaTusChxoaPSKMdMas')
    from_pub = from_private_key.get_public_key()  # 必须从私钥派生公钥，不能直接使用地址
    
    # 获取脚本代码
    script_code = from_pub.get_segwit_address().to_script_pub_key()  # 使用从公钥派生的脚本代码，这是 SegWit 交易的要求
    
    # 发送方信息（SegWit 地址）
    from_address = from_pub.get_segwit_address()
    
    # 添加私钥验证
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {from_private_key.to_wif()}")
    print(f"Generated address: {from_private_key.get_public_key().get_segwit_address().to_string()}")
    print(f"Expected address: tb1q840vrzv5lfuj5m6udgc3p75m0uk888w0daves5")
    
    # 接收方信息（ Legacy 地址）
    # to_address = P2pkhAddress('mfaYiTEs7zkBNjTMaB42THkbWmkzj5aqTy')
    # 接收方信息（ Taproot 地址）
    to_address = P2trAddress('tb1p9q80mtqns48e8dm4gkuq0n5tx9zdwqqqh9skyagqrtq3q7jvdqfqe02xas')

    
    print(f"\n发送方 Segwit 地址: {from_address.to_string()}")
    print(f"接收方 Legacy 地址: {to_address.to_string()}")
    
    # 创建交易输入
    txin = TxInput(
        '8a2d88df7465ea15a9f5a040c4ed7a1ecda633a657c6b3ba41a4713f6a26a800',  # 前一个交易的ID
        3  # vout
    )
    
    # 计算金额（单位：BTC）
    total_input = 0.00001  # 输入金额
    amount_to_send = 0.000005   # 发送金额
    fee = 0.000004         # 手续费
    # 找零
    change_amount = total_input - amount_to_send - fee

    # 创建交易输出
    txout = TxOutput(to_satoshis(amount_to_send), to_address.to_script_pub_key())
    change_output = TxOutput(to_satoshis(change_amount), from_address.to_script_pub_key())
    
    # 创建交易
    tx = Transaction([txin], [txout, change_output], has_segwit=True)  # SegWit 交易必须设置 has_segwit=True
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 签名交易
    sig = from_private_key.sign_segwit_input(  # 使用 sign_segwit_input 而不是 sign_input
        tx,
        0,
        script_code,  # 使用从公钥派生的脚本代码，这是验证规则所需
        to_satoshis(total_input)  # SegWit 交易必须提供输入金额
    )
    
    # 获取公钥
    public_key = from_private_key.get_public_key().to_hex()
        
    # 设置赎回脚本
    txin.script_sig = Script([])  # SegWit 交易的 script_sig 必须为空
    
    # 设置见证数据
    tx.witnesses.append(TxWitnessInput([sig, public_key]))  # 使用 TxWitnessInput 包装见证数据
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从地址: {from_address.to_string()}")
    print(f"到地址: {to_address.to_string()}")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {fee} BTC")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main()
    # 交易url： https://mempool.space/testnet/tx/43b4ce7070e74bee6ef3595f9a0a24e6a75089095fed74a4d658e7e772a35c32