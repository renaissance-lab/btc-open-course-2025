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
from bitcoinutils.script import Script
from bitcoinutils.keys import P2pkhAddress
import requests

def main():
    # 设置测试网
    setup('testnet')
    
    # 1. legacy
    # 发送方信息（使用正确的私钥）
    legacy_from_private_key = PrivateKey('cVHfvGCzJBkGXHmpLS1H87xrgv5R6xodaoqNmAcpp6NLMGJjq9yt')
    legacy_from_pub = legacy_from_private_key.get_public_key()
    legacy_from_address = legacy_from_pub.get_address()
    
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {legacy_from_private_key.to_wif()}")
    print(f"Generated address: {legacy_from_address.to_string()}")
    print(f"Expected address: mm46s3okAgjMrTWkFQnwchNNea39E4CmQw")
    
    legacy_input = TxInput(
        '6f14be3c9cb12cc04abf5707d82fe8c0fc6a43e11a55acf526e47f44f756ea84',
        0
    )
    legacy_amount = 0.00000700
    
    # 2. segwit
    # 发送方信息（使用正确的私钥）
    segwit_from_private_key = PrivateKey('cSbxcaZFK4Yeq95EJ9H2EbNJfY6gNhdTe8TCTZmReVUtMXvofq1p')
    segwit_from_pub = segwit_from_private_key.get_public_key()  # 必须从私钥派生公钥，不能直接使用地址
    
    # 发送方信息（SegWit 地址）
    segwit_from_address = segwit_from_pub.get_segwit_address()
    
    # 获取脚本代码
    segwit_script_code = segwit_from_address.to_script_pub_key()  # 使用从公钥派生的脚本代码，这是 SegWit 交易的要求
    
    # 添加私钥验证
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {segwit_from_private_key.to_wif()}")
    print(f"Generated address: {segwit_from_address.to_string()}")
    print(f"Expected address: tb1q3jg3jgdydh3s9j2hrgqksg6gnws06znz2rwmda")
    
    segwit_input = TxInput(
        'bbf77a5980cfc8ff45ebd6f3d3c07cfd256867bedc8666536f413690a28c6f48',
        0
    )
    
    segwit_amount = 0.00000995
    
    # 3. taproot
    # 发送方信息（使用正确的私钥）
    taproot_from_private_key = PrivateKey('cNUUxnhdmwhbzryAEstuf1yieo8EDiGTkCeAEHB15vbB9rdtnUxL')
    taproot_from_pub = taproot_from_private_key.get_public_key()
    taproot_from_address = taproot_from_pub.get_taproot_address()
    
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {taproot_from_private_key.to_wif()}")
    print(f"Generated address: {taproot_from_address.to_string()}")
    print(f"Expected address: tb1p369rg75827p8pz7kgt0kc4lljyctffpt0cl6rftwtzenmswdkalsctfyl6")
    
    # 创建交易输入
    taproot_input = TxInput(
        '30db2ab4cf6c66c202943608375c67212d3574926b7ab4862c5a98882bfb1d61',
        0
    )
    
    taproot_amount = 0.00008500
    
     # 接收方地址
    to_address = P2trAddress('tb1p369rg75827p8pz7kgt0kc4lljyctffpt0cl6rftwtzenmswdkalsctfyl6')
    
    total_amount = legacy_amount + segwit_amount + taproot_amount
    send_amount = total_amount - 0.000004
    txout = TxOutput(
        to_satoshis(send_amount),
        to_address.to_script_pub_key()
    )
    
    tx = Transaction([legacy_input, segwit_input, taproot_input], [txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())
    
    # 收集所有输入的脚本代码和金额（对于Taproot签名必需）
    legacy_script = legacy_from_pub.get_address().to_script_pub_key()
    segwit_script = segwit_from_pub.get_segwit_address().to_script_pub_key()
    taproot_script = taproot_from_address.to_script_pub_key()
    
    # 所有输入的脚本代码列表
    all_scripts = [legacy_script, segwit_script, taproot_script]
    
    # 所有输入的金额列表（转换为satoshis）
    all_amounts = [to_satoshis(legacy_amount), to_satoshis(segwit_amount), to_satoshis(taproot_amount)]
    
    print("\n准备签名交易...")
    
    # 1. 先签名 Legacy 输入（索引 0）
    legacy_sig = legacy_from_private_key.sign_input(tx, 0, legacy_script)
    legacy_pk = legacy_from_private_key.get_public_key().to_hex()
    legacy_input.script_sig = Script([legacy_sig, legacy_pk])
    
    # 2. 签名 Segwit 输入（索引 1）
    segwit_script_code = segwit_from_pub.get_address().to_script_pub_key()
    segwit_sig = segwit_from_private_key.sign_segwit_input(
        tx, 
        1, 
        segwit_script_code, 
        all_amounts[1]
    )
    segwit_pk = segwit_from_private_key.get_public_key().to_hex()
    segwit_input.script_sig = Script([])
    
    # 3. 签名 Taproot 输入（索引 2）
    print(f"Input script: {taproot_script}")
    taproot_sig = taproot_from_private_key.sign_taproot_input(
        tx,
        2,
        all_scripts,  # 传递所有输入的脚本代码
        all_amounts    # 传递所有输入的金额
    )
    
    # 添加见证数据，与输入顺序严格对应
    tx.witnesses = []
    tx.witnesses.append(TxWitnessInput([]))  # 输入0: Legacy 使用空见证
    tx.witnesses.append(TxWitnessInput([segwit_sig, segwit_pk]))  # 输入1: Segwit 见证
    tx.witnesses.append(TxWitnessInput([taproot_sig]))  # 输入2: Taproot 见证
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"Legacy 地址: {legacy_from_address.to_string()}")
    print(f"Segwit 地址: {segwit_from_address.to_string()}")
    print(f"Taproot 地址: {taproot_from_address.to_string()}")
    print(f"到地址 (P2TR): {to_address.to_string()}")
    print(f"发送金额: {send_amount} BTC")
    print(f"手续费: {total_amount - send_amount} BTC")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    
    print("\n广播交易...")
    mempool_api = "https://mempool.space/testnet/api/tx"
    try:
        response = requests.post(mempool_api, data=signed_tx)
        if response.status_code == 200:
            txid = response.text
            print(f"交易成功！")
            print(f"交易ID: {txid}")
            print(f"查看交易: https://mempool.space/testnet/tx/{txid}")
        else:
            print(f"广播失败: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
        
    # 查看交易: https://mempool.space/testnet/tx/ab48cefb3ea411a7a7ac1a77a7f78f365ab603e028621b7a890b81cd9ca95fc8


if __name__ == "__main__":
    main() 