"""
从 Taproot 地址转账到 Taproot 地址 

交易结构说明：
1. 输入 (P2TR):
   - 来源地址: tb1p060z97qusuxe7w6h8z0l9kam5kn76jur22ecel75wjlmnkpxtnls6vdgne
   - 金额: 0.00022799 tBTC
   - 锁定脚本: OP_1 <32字节公钥>

2. 输出 (P2TR):
   - 目标地址: tb1pqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesf3hn0c
   - 发送金额: 0.00021799 tBTC
   - 手续费: 0.00001 tBTC



交易成功了
e44de515c1da67b6f8febf01acbd4e3be6d04a49deffae6671d2406382789d71

Taproot 和 普通 Segwit (P2WPKH) 的见证数据确实有很大区别：
Witness:
304402203569b75b530232ccb3813cac9fb2e3ee1a5e00fe7ec1994393691e7054e2772f02202a95dfa8fef7a33ebcc9b8c043d43677f74705c6c7ff76312c30901baa28ec1e01  (签名，约71字节)
0250be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d3    (公钥，33字节)

Taproot 的见证数据:
Witness:
76ea0e3046f5ed690debb21f4afb77f68aca278fc71251b6ef50554f910adbe8551775641b78a7424659d752e037a48a80b1ecfff4787c09da5d5928d06daf0d  (仅签名，64字节)
主要区别：
签名算法:
P2WPKH: 使用 ECDSA 签名（约71字节）
Taproot: 使用 Schnorr 签名（固定64字节）
见证结构:
P2WPKH: 需要签名 + 公钥
Taproot: 只需要签名（公钥已在输出脚本中）
优势:
Taproot 的见证数据更小，节省交易费
Schnorr 签名提供更好的隐私性
支持更复杂的智能合约
这就是为什么 Taproot 交易的见证数据看起来更简洁，这也是比特币网络的一个重要升级。
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息（使用正确的私钥）
    # 发送方地址: tb1p060z97qusuxe7w6h8z0l9kam5kn76jur22ecel75wjlmnkpxtnls6vdgne
    from_private_key = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_taproot_address()
    
    # 接收方地址
    to_address = P2trAddress('tb1plzj3umwlvva50tvm5ugja6gvexd9yy5pmy0r5nqm5hu6g8p848hs9x0jwr')
    
    # 创建交易输入
    txin = TxInput(
        '6d2b74fa6e7b47f4a2d2cb9ea2d3226f89ae781ef739a8f7ae36e18ae116256c',
        0
    )
    
    # 输入金额（用于签名）
    input_amount = 0.00001700
    amounts = [to_satoshis(input_amount)]
    
    # 输入脚本（用于签名）
    input_script = from_address.to_script_pub_key()
    scripts = [input_script]
    
    # 创建交易输出
    amount_to_send = 0.00001500
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )
    
    # 创建交易（启用 segwit）
    tx = Transaction([txin], [txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())
    
    # 签名交易
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        scripts,
        amounts
    )
    
    # 添加见证数据
    tx.witnesses.append(TxWitnessInput([sig]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从地址 (P2TR): {from_address.to_string()}")
    print(f"到地址 (P2TR): {to_address.to_string()}")
    print(f"发送金额: {amount_to_send} BTC")
    print(f"手续费: {input_amount - amount_to_send} BTC")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 