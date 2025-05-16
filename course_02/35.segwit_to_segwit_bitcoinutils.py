from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
# from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2wpkhAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息
    from_private_key = PrivateKey('cThG187gvrsZwnzsmPZiHW58hrhGKrfMdhAtEZKQxmwgKEdQsQ2h')
    from_pub = from_private_key.get_public_key()  # 必须从私钥派生公钥，不能直接使用地址
    
    # 获取脚本代码
    script_code = from_pub.get_address().to_script_pub_key()  # 使用从公钥派生的脚本代码，这是 SegWit 交易的要求
    
    # 发送方信息（SegWit 地址）
    from_address = P2wpkhAddress('tb1q840vrzv5lfuj5m6udgc3p75m0uk888w0daves5')
    
    # 添加私钥验证
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {from_private_key.to_wif()}")
    print(f"Generated address: {from_private_key.get_public_key().get_segwit_address().to_string()}")
    print(f"Expected address: tb1q840vrzv5lfuj5m6udgc3p75m0uk888w0daves5")
    
    # 接收方信息（SegWit 地址）
    to_address = P2wpkhAddress('tb1qu3d70dmmalv6vcm0279mmvzxxsd5aeu4f2zfwd')
    
    print(f"\n发送方 Segwit 地址: {from_address.to_string()}")
    print(f"接收方 Segwit 地址: {to_address.to_string()}")
    
    # 创建交易输入
    txin = TxInput(
        'bb13224a3b8771f5a2637053b07c6e1e028db0a26b3cc4ccb96ebb7eb750ae4b',  # 前一个交易的ID
        0  # vout
    )
    
    # 计算金额（单位：BTC）
    total_input = 0.00128800  # 输入金额
    amount_to_send = 0.00128500   # 发送金额
    fee = 0.00000300         # 手续费
    
    # 创建交易输出
    txout = TxOutput(to_satoshis(amount_to_send), to_address.to_script_pub_key())
    
    # 创建交易
    tx = Transaction([txin], [txout], has_segwit=True)  # SegWit 交易必须设置 has_segwit=True
    
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