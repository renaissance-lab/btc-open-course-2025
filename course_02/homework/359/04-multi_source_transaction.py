"""
多来源交易构建

实现一个比特币交易，从三种不同类型的地址（legacy、segwit、taproot）获取UTXO作为输入，
然后将资金支付到一个目标地址，并自动计算手续费，将输入金额减去手续费作为输出金额。

"""

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress, P2trAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.utils import to_satoshis
import requests

# 设置测试网
setup('testnet')

# 定义三种不同类型的钱包（私钥和地址）
def create_wallets():
    # Legacy钱包
    legacy_private_key = PrivateKey('cV65Dv7Kwq8m1pG8c48UgWgx5J1Tv1TBeoTdDeVRjmQ5CpKkuPw6')
    legacy_public_key = legacy_private_key.get_public_key()
    legacy_address = legacy_public_key.get_address()
    
    # SegWit钱包
    segwit_private_key = PrivateKey('cThG187gvrsZwnzsmPZiHW58hrhGKrfMdhAtEZKQxmwgKEdQsQ2h')
    segwit_public_key = segwit_private_key.get_public_key()
    segwit_address = segwit_public_key.get_segwit_address()
    
    # Taproot钱包
    taproot_private_key = PrivateKey('cPeon9fBsW2BxwJTALj3hGzh9vm8C52Uqsce7MzXGS1iFJkPF4AT')
    taproot_public_key = taproot_private_key.get_public_key()
    taproot_address = taproot_public_key.get_taproot_address()
    
    # 目标地址（这里使用SegWit地址作为示例）
    destination_address = P2wpkhAddress('tb1qu3d70dmmalv6vcm0279mmvzxxsd5aeu4f2zfwd')
    
    return {
        'legacy': {
            'private_key': legacy_private_key,
            'address': legacy_address
        },
        'segwit': {
            'private_key': segwit_private_key,
            'address': segwit_address
        },
        'taproot': {
            'private_key': taproot_private_key,
            'address': taproot_address
        },
        'destination': destination_address
    }

# 获取UTXO信息
def get_utxos(wallets):
    return {
        'legacy': {
            'txid': 'e9345c73c7496bb78477d5c98c955c7691952e6596e56246871b1bd09eb460d7',
            'vout': 0,
            'amount': 0.00001000  # 以BTC为单位
        },
        'segwit': {
            'txid': 'bb13224a3b8771f5a2637053b07c6e1e028db0a26b3cc4ccb96ebb7eb750ae4b',
            'vout': 0,
            'amount': 0.00001200  # 以BTC为单位
        },
        'taproot': {
            'txid': '69d286af55274bdfaed7636cfcee6ddee313e0986f6791f2e84c7bf479ffa1e4',
            'vout': 0,
            'amount': 0.00000400  # 以BTC为单位
        }
    }

# 估算交易大小和手续费
def estimate_fee(utxos, fee_rate=10):
    # 估算交易大小（字节）
    # 基本交易结构：约10字节
    # 每个输入：Legacy约148字节，SegWit约68字节，Taproot约57字节
    # 每个输出：约34字节
    base_size = 10
    legacy_input_size = 148
    segwit_input_size = 68
    taproot_input_size = 57
    output_size = 34
    
    # 计算总大小
    total_size = base_size
    total_size += legacy_input_size + segwit_input_size + taproot_input_size
    total_size += output_size  # 一个输出
    
    # 计算手续费（satoshis）
    fee = total_size * fee_rate
    
    return fee / 100000000  # 转换为BTC

# 构建并签名交易
def create_transaction(wallets, utxos):
    # 计算总输入金额
    total_input = utxos['legacy']['amount'] + utxos['segwit']['amount'] + utxos['taproot']['amount']
    
    # 估算手续费
    fee = estimate_fee(utxos)
    
    # 计算输出金额
    output_amount = total_input - fee
    
    print(f"总输入金额: {total_input} BTC")
    print(f"估算手续费: {fee} BTC")
    print(f"输出金额: {output_amount} BTC")
    
    # 创建交易输入
    inputs = []
    
    # Legacy输入
    legacy_txin = TxInput(utxos['legacy']['txid'], utxos['legacy']['vout'])
    inputs.append(legacy_txin)
    
    # SegWit输入
    segwit_txin = TxInput(utxos['segwit']['txid'], utxos['segwit']['vout'])
    inputs.append(segwit_txin)
    
    # Taproot输入
    taproot_txin = TxInput(utxos['taproot']['txid'], utxos['taproot']['vout'])
    inputs.append(taproot_txin)
    
    # 创建交易输出
    outputs = []
    
    # 目标输出
    destination_script = wallets['destination'].to_script_pub_key()
    outputs.append(TxOutput(to_satoshis(output_amount), destination_script))
    
    # 创建交易
    tx = Transaction(inputs, outputs)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 签名Legacy输入
    legacy_private_key = wallets['legacy']['private_key']
    legacy_address = wallets['legacy']['address']
    legacy_script = legacy_address.to_script_pub_key()
    
    # Legacy签名
    legacy_sig = legacy_private_key.sign_input(tx, 0, legacy_script)
    legacy_pubkey = legacy_private_key.get_public_key().to_hex()
    inputs[0].script_sig = Script([legacy_sig, legacy_pubkey])
    
    # 签名SegWit输入
    segwit_private_key = wallets['segwit']['private_key']
    segwit_public_key = segwit_private_key.get_public_key()
    segwit_script_code = segwit_public_key.get_address().to_script_pub_key()
    
    # 输入金额（用于签名）
    segwit_input_amount = utxos['segwit']['amount']
    segwit_amount = to_satoshis(segwit_input_amount)
    
    # SegWit签名
    segwit_sig = segwit_private_key.sign_segwit_input(
        tx,
        1,
        segwit_script_code,
        segwit_amount
    )
    segwit_pubkey = segwit_private_key.get_public_key().to_hex()
    inputs[1].script_sig = Script([])
    tx.witnesses.append(TxWitnessInput([segwit_sig, segwit_pubkey]))
    
    # 签名Taproot输入
    taproot_private_key = wallets['taproot']['private_key']
    taproot_address = wallets['taproot']['address']
    taproot_script = taproot_address.to_script_pub_key()
    
    # 输入金额（用于签名）
    taproot_input_amount = utxos['taproot']['amount']
    taproot_amounts = [to_satoshis(taproot_input_amount)]
    
    # 输入脚本（用于签名）
    taproot_scripts = [taproot_script]
    
    # Taproot签名
    taproot_sig = taproot_private_key.sign_taproot_input(
        tx,
        2,
        taproot_scripts,
        taproot_amounts
    )
    
    # Taproot输入的脚本为空，见证数据单独存储
    inputs[2].script_sig = Script([])
    tx.witnesses.append(TxWitnessInput([taproot_sig]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    return signed_tx

# 广播交易
def broadcast_transaction(signed_tx):
    print("\n广播交易...")
    print("注意：这是一个演示，实际广播需要有效的UTXO")
    print("手动广播:")
    print("https://mempool.space/testnet/tx/push")
    

# 主函数
def main():
    print("=== 多来源交易构建 ===\n")
    
    # 创建钱包
    wallets = create_wallets()
    
    print("钱包地址:")
    print(f"Legacy地址: {wallets['legacy']['address'].to_string()}")
    print(f"SegWit地址: {wallets['segwit']['address'].to_string()}")
    print(f"Taproot地址: {wallets['taproot']['address'].to_string()}")
    print(f"目标地址: {wallets['destination'].to_string()}")
    
    # 获取UTXO
    utxos = get_utxos(wallets)
    
    print("\nUTXO信息:")
    for addr_type, utxo in utxos.items():
        print(f"{addr_type.capitalize()} UTXO: {utxo['txid']}:{utxo['vout']} - {utxo['amount']} BTC")
    
    # 创建交易
    print("\n创建交易...")
    signed_tx = create_transaction(wallets, utxos)
    
    # 广播交易
    broadcast_transaction(signed_tx)


if __name__ == "__main__":
    main()