"""
Taproot到SegWit和Legacy地址的比特币交易

本文件实现从Taproot地址向SegWit和Legacy地址发送比特币的交易。

Legacy地址: mgMzeGduaTgTAywnq9BND2Ard4iSPLxqoW
SegWit地址: tb1qp9r90d87wlwt9730r4u58gm3qz8wjw4ha2jdp8
Taproot地址: tb1p52hq8twkndu4awmex58xykjv8xj2c467j0r2dvj8y89ndfme09kss2w7ya

私钥(HEX): 2caadc4e587783ad34753f109fae2de63d71a2993f3c258cc4d5fc647da8a3a5
私钥(WIF): cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6
公钥(压缩),字节: b'\x03R\x94\x95h\xd4<\xa8~\xf0\xa00\xf9\xc4+\xb2\xbf\xdeX\xe0\xc4\xae\xba\x03U\xfd\xcbQ\xc5\x05s\x00m'
公钥(压缩): 0352949568d43ca87ef0a030f9c42bb2bfde58e0c4aeba0355fdcb51c50573006d
公钥(未压缩): 0452949568d43ca87ef0a030f9c42bb2bfde58e0c4aeba0355fdcb51c50573006d2515834fc3c31813e37d10ca7e96183329c6c8b3379d741522a620416dc48923

https://mempool.space/testnet/tx/c05341be4dcb146f96c11da93768eb2473bcbf4eaeda182ae0805e75130e80bc
"""

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import to_satoshis

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息（Taproot地址）
    from_private_key = PrivateKey('cP5XejkeNHytd3H8mNBj73N1c6Ve7pYi17kPC7nmd3ricXVZYnz6')
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_taproot_address()
    
    # 接收方信息（SegWit地址）
    to_segwit_address = P2wpkhAddress('tb1qu3d70dmmalv6vcm0279mmvzxxsd5aeu4f2zfwd')
    
    # 接收方信息（Legacy地址）
    to_legacy_address = P2pkhAddress('mkDeKvM5BwXHt4SDLxE5kjwDiNtc8UUzmC')
    
    print(f"\n发送方 Taproot 地址: {from_address.to_string()}")
    print(f"接收方 SegWit 地址: {to_segwit_address.to_string()}")
    print(f"接收方 Legacy 地址: {to_legacy_address.to_string()}")
    
    # 创建交易输入
    txin = TxInput(
        '8dadead937481f1bfa41dd5f07c4ca538b3be9b03e600ae803f4a5d8ad82e0b2',  # 前一个交易的ID
        1  # vout
    )
    
    # 计算金额（单位：BTC）
    total_input = 0.00121110  # 输入金额
    fee = 0.00000200         # 手续费
    amount_to_send = (total_input - fee) / 2  # 平分发送金额到两个地址
    
    # 创建交易输出
    txout1 = TxOutput(to_satoshis(amount_to_send), to_segwit_address.to_script_pub_key())
    txout2 = TxOutput(to_satoshis(amount_to_send), to_legacy_address.to_script_pub_key())
    
    # 创建交易
    tx = Transaction([txin], [txout1, txout2], has_segwit=True)  # Taproot 交易必须设置 has_segwit=True
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 获取输入脚本
    input_script = from_address.to_script_pub_key()
    scripts = [input_script]
    
    # 输入金额（用于签名）
    amounts = [to_satoshis(total_input)]
    
    # 签名交易
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        scripts,
        amounts
    )
    
    # 设置赎回脚本
    txin.script_sig = Script([])  # Taproot 交易的 script_sig 必须为空
    
    # 设置见证数据
    tx.witnesses.append(TxWitnessInput([sig]))  # Taproot 只需要签名
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从地址: {from_address.to_string()} (Taproot)")
    print(f"到SegWit地址: {to_segwit_address.to_string()}")
    print(f"到Legacy地址: {to_legacy_address.to_string()}")
    print(f"每个地址发送金额: {amount_to_send} BTC")
    print(f"总发送金额: {amount_to_send * 2} BTC")
    print(f"手续费: {fee} BTC")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")
    
if __name__ == "__main__":
    main()