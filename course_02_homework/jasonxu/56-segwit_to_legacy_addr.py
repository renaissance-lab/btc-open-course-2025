from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
# from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2wpkhAddress, PrivateKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
import os, sys
import configparser
import requests

conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)


def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息
    from_private_key = PrivateKey(conf.get("testnet3", "private_key_wif"))
    from_pub = from_private_key.get_public_key()  # 必须从私钥派生公钥，不能直接使用地址
    
    # 获取脚本代码
    script_code = from_pub.get_address().to_script_pub_key()  # 使用从公钥派生的脚本代码，这是 SegWit 交易的要求
    
    # 发送方信息（SegWit 地址）
    from_address = P2wpkhAddress(conf.get("testnet3", "segwit_address"))
    
    # 添加私钥验证
    print("\n=== 验证私钥 ===")
    print(f"Private key WIF: {from_private_key.to_wif()}")
    print(f"Generated address: {from_private_key.get_public_key().get_segwit_address().to_string()}")
    
    # 接收方信息（p2pkh 地址）
    to_address = P2pkhAddress(conf.get("testnet3", "legacy_address"))
    
    print(f"\n发送方 Segwit 地址: {from_address.to_string()}")
    print(f"接收方 legacy 地址: {to_address.to_string()}")
    
    # 创建交易输入
    txin = TxInput(
        'dcd1ba49acbaf58be1197c6f20513dd69d24ebb5a2a73174a2ac08c9cd3e77e3',  # 前一个交易的ID
        0  # vout
    )
    
    # 计算金额（单位：BTC）
    total_input = 0.00002000  # 输入金额
    amount_to_send = 0.00001800   # 发送金额
    fee = 0.00000200         # 手续费
    
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

    # 6. 广播交易
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

if __name__ == "__main__":
    main() 