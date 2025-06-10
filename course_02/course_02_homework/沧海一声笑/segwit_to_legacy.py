from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.keys import P2wpkhAddress, PrivateKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput

def main():
    # 设置 regtest 网络
    setup('regtest')
    
    # 发送方信息
    from_private_key = PrivateKey('cRN6iYkJookUYiBH32PWyaf1arRDGq6gDbw7QRi3R5b2nPJdnkuv')
    from_pub = from_private_key.get_public_key()
    
    # 获取脚本代码
    script_code = from_pub.get_address().to_script_pub_key()
    
    # 发送方信息（SegWit 地址）
    from_address = P2wpkhAddress('bcrt1qj5q6huak207m39d4g3x33asyywdph4ytqlawvn')
    
    # 添加私钥验证
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {from_private_key.to_wif()}")
    print(f"Generated address: {from_private_key.get_public_key().get_segwit_address().to_string()}")
    print(f"Expected address: bcrt1qj5q6huak207m39d4g3x33asyywdph4ytqlawvn")
    
    # 接收方信息（Legacy 地址）
    to_address = P2pkhAddress('moyxCWpvEg9w5gGGV3XVEGwQXttDdtoEkc')
    
    print(f"\n发送方 Segwit 地址: {from_address.to_string()}")
    print(f"接收方 Legacy 地址: {to_address.to_string()}")
    
    # 创建交易输入
    txin = TxInput(
        '762679aa8dddf7dcd30367a36e1e235518b334ae8a6963d72f25c9d45509b3fe',  # 前一个交易的ID
        0  # vout
    )
    
    # 计算金额（单位：BTC）
    total_input = 0.78125000  # 输入金额
    amount_to_send = 0.5      # 发送金额
    fee = 0.00001000         # 手续费 (1000 聪)
    
    # 创建交易输出
    txout = TxOutput(to_satoshis(amount_to_send), to_address.to_script_pub_key())
    
    # 创建找零输出
    change_amount = total_input - amount_to_send - fee
    change_txout = TxOutput(to_satoshis(change_amount), from_address.to_script_pub_key())
    
    # 创建交易
    tx = Transaction([txin], [txout, change_txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 签名交易
    sig = from_private_key.sign_segwit_input(
        tx,
        0,
        script_code,
        to_satoshis(total_input)
    )
    
    # 获取公钥
    public_key = from_private_key.get_public_key().to_hex()
        
    # 设置赎回脚本
    txin.script_sig = Script([])
    
    # 设置见证数据
    tx.witnesses.append(TxWitnessInput([sig, public_key]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从地址: {from_address.to_string()}")
    print(f"到地址: {to_address.to_string()}")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {fee} BTC")
    print(f"找零金额: {change_amount} BTC")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 