from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2trAddress, P2wpkhAddress, P2pkhAddress
import os, sys
import configparser
import requests

conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

def main():
    # 设置测试网
    setup('testnet')
    
    # 发送方信息（使用正确的私钥）
    from_private_key = PrivateKey(conf.get("testnet3", "private_key_wif"))
    from_pub = from_private_key.get_public_key()
    from_address = from_pub.get_taproot_address()
    
    # 创建交易输入
    txin = TxInput(
        'b99c6efe0686649b02c9e991b37d35004e91594fd19dda797ac502ed20b5021b',
        1
    )
    
    # 输入金额（用于签名）
    input_amount = 13800
    amounts = [input_amount]
    output_amount = 10000
    fee = 100

    
    # 输入脚本（用于签名）
    input_script = from_address.to_script_pub_key()
    scripts = [input_script]
    
    # 创建交易输出
    segwit_addr = P2wpkhAddress(conf.get("testnet3", "segwit_address"))
    txout = TxOutput(
        output_amount, segwit_addr.to_script_pub_key()
    )

    legacy_addr = P2pkhAddress(conf.get("testnet3", "legacy_address"))
    change_txout = TxOutput(input_amount-output_amount-fee, 
                            legacy_addr.to_script_pub_key()
                            )
 
    
    # 创建交易（启用 segwit）
    tx = Transaction([txin], [txout, change_txout], has_segwit=True)
    
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
    print(f"发送金额: {output_amount} BTC")
    print(f"手续费: {fee}")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")

    fee = int(tx.get_vsize() *1.05)
    print(f"重新计算手续费: {fee}")
    change_txout = TxOutput(input_amount-output_amount-fee, 
                            legacy_addr.to_script_pub_key()
                            )
    tx = Transaction([txin], [txout, change_txout], has_segwit=True)
    sig = from_private_key.sign_taproot_input(
        tx,
        0,
        scripts,
        amounts
    )       
    # 添加见证数据
    tx.witnesses.append(TxWitnessInput([sig]))
    signed_tx = tx.serialize()
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")

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