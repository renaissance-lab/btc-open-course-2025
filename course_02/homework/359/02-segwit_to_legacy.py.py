"""
SegWit到Legacy地址的比特币交易

本文件实现从SegWit地址向Legacy地址发送比特币的交易。

Legacy地址: mgMzeGduaTgTAywnq9BND2Ard4iSPLxqoW
SegWit地址: tb1qp9r90d87wlwt9730r4u58gm3qz8wjw4ha2jdp8
Taproot地址: tb1p52hq8twkndu4awmex58xykjv8xj2c467j0r2dvj8y89ndfme09kss2w7ya

私钥(HEX): 2caadc4e587783ad34753f109fae2de63d71a2993f3c258cc4d5fc647da8a3a5
私钥(WIF): cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6
公钥(压缩),字节: b'\x03R\x94\x95h\xd4<\xa8~\xf0\xa00\xf9\xc4+\xb2\xbf\xdeX\xe0\xc4\xae\xba\x03U\xfd\xcbQ\xc5\x05s\x00m'
公钥(压缩): 0352949568d43ca87ef0a030f9c42bb2bfde58e0c4aeba0355fdcb51c50573006d
公钥(未压缩): 0452949568d43ca87ef0a030f9c42bb2bfde58e0c4aeba0355fdcb51c50573006d2515834fc3c31813e37d10ca7e96183329c6c8b3379d741522a620416dc48923

https://mempool.space/testnet/tx/10c3b74dc4f9ba517ae199d24346dcb0eb1320ac878488943a557c728ba50e11
"""
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.keys import P2wpkhAddress, PrivateKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息
    from_private_key = PrivateKey('cTeSvY5tq6CmPXcrr9puFsxgd3tHH2P5uoW3SYcMLVFBGhY2qExY')
    from_pub = from_private_key.get_public_key()  # 必须从私钥派生公钥，不能直接使用地址
    
    # 获取脚本代码
    script_code = from_pub.get_address().to_script_pub_key()  # 使用从公钥派生的脚本代码，这是 SegWit 交易的要求
    
    # 发送方信息（SegWit 地址）
    from_address = from_pub.get_segwit_address()
    
    to_address = P2pkhAddress('mgMzeGduaTgTAywnq9BND2Ard4iSPLxqoW')
    
    print(f"\n发送方 Segwit 地址: {from_address.to_string()}")
    print(f"接收方 Segwit 地址: {to_address.to_string()}")
    
    # 创建交易输入
    txin = TxInput(
        '55ed86bd3675f903c811bc703c19791c184ea54fc880ac4c22f9f3fab505b222',
        0  # vout
    )
    
   # 计算金额（单位：BTC）
    total_input = 0.00190800  # 输入金额
    amount_to_send = 0.00190600   # 发送金额

    
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
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 