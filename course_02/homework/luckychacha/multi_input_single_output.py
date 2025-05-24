# 多种输入类型（legacy、segwit、taproot）到legacy地址的转账代码
# 交易 hash https://mempool.space/testnet/tx/9c0787a56b7e7154acd2dde72a3cb5ffe7e23ed6c4196d71b722438dab8ec7ce
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.script import Script
from utils import BitcoinAddressInfo
import requests

def main():
    # 设置测试网
    setup('testnet')
    
    # 私钥
    from_private_key = PrivateKey('cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh')
    from_pub = from_private_key.get_public_key()
    
    # 从同一私钥生成3种不同类型的地址
    legacy_address = from_pub.get_address()
    segwit_address = from_pub.get_segwit_address()
    taproot_address = from_pub.get_taproot_address()
    
    # 接收方地址（Legacy）
    
    # 显示各种地址信息
    print("\n=== 地址信息 ===")
    print(f"私钥 WIF: {from_private_key.to_wif()}")
    print(f"Legacy 地址: {legacy_address.to_string()}")
    print(f"SegWit 地址: {segwit_address.to_string()}")
    print(f"Taproot 地址: {taproot_address.to_string()}")

    util = BitcoinAddressInfo()

    legacy_amount = 0
    legacy_txid = ''
    legacy_vout = 0
    legacy_utxos = util.get_address_utxos(legacy_address.to_string())
    for utxo in legacy_utxos:
        legacy_amount += to_satoshis(utxo['value'])
        legacy_txid = utxo['txid']
        legacy_vout = utxo['vout']
        print("legacy_utxo:", utxo)
        break

    segwit_amount = 0
    segwit_txid = ''
    segwit_vout = 0
    segwit_utxos = util.get_address_utxos(segwit_address.to_string())
    for utxo in segwit_utxos:
        segwit_amount += to_satoshis(utxo['value'])
        segwit_txid = utxo['txid']
        segwit_vout = utxo['vout']
        print("segwit_utxo:", utxo)
        break

    taproot_amount = 0
    taproot_txid = ''
    taproot_vout = 0
    taproot_utxos = util.get_address_utxos(taproot_address.to_string())
    for utxo in taproot_utxos:
        taproot_amount += to_satoshis(utxo['value'])
        taproot_txid = utxo['txid']
        taproot_vout = utxo['vout']
        print("taproot_utxo:", utxo)
        break
    
    if legacy_amount == 0 or segwit_amount == 0 or taproot_amount == 0:
        print("没有足够的UTXO")
        return
    
    # legacy_amount = to_satoshis(0.00014800)
    # segwit_amount = to_satoshis(0.00014800)
    # taproot_amount = to_satoshis(0.00001)
    
    # 计算总输入金额
    total_input = legacy_amount + segwit_amount + taproot_amount
    
    # 设置手续费
    fee = to_satoshis(0.000008)  # 0.000004 BTC
    # fee = to_satoshis(estimate_fee())
    
    # 计算发送金额
    amount_to_send = total_input - fee

    # 创建多个交易输入
    txin_legacy = TxInput(legacy_txid, legacy_vout)
    txin_segwit = TxInput(segwit_txid, segwit_vout)
    txin_taproot = TxInput(taproot_txid, taproot_vout)
    txinputs = [txin_legacy, txin_segwit, txin_taproot]

    # 创建3个交易输出
    avg_amount = int(amount_to_send/3)
    print("avg_amount:", avg_amount)
    txout = TxOutput(amount_to_send, taproot_address.to_script_pub_key())
    # txout2 = TxOutput(avg_amount, segwit_address.to_script_pub_key())
    # txout3 = TxOutput(avg_amount, taproot_address.to_script_pub_key())
    
    # 创建交易
    tx = Transaction(txinputs, [txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 准备所有脚本和金额数组（按照新脚本方式）
    legacy_script = legacy_address.to_script_pub_key()
    # 从公钥派生脚本，因为地址是segwit地址
    segwit_script = from_pub.get_address().to_script_pub_key()
    taproot_script = taproot_address.to_script_pub_key()

    utxos_script_pubkeys = [legacy_script, segwit_address.to_script_pub_key(), taproot_script]
    amounts = [legacy_amount, segwit_amount, taproot_amount]
    
    # 签名所有输入
    sig1 = from_private_key.sign_input(tx, 0, legacy_script)
    sig2 = from_private_key.sign_segwit_input(tx, 1, segwit_script, amounts[1])
    sig3 = from_private_key.sign_taproot_input(tx, 2, utxos_script_pubkeys, amounts)

    # Legacy输入使用script_sig
    txinputs[0].script_sig = Script([sig1, from_pub.to_hex()])
    # SegWit输入使用空script_sig
    txinputs[1].script_sig = Script([])
    # Taproot输入使用空script_sig
    txinputs[2].script_sig = Script([])
    
    # 设置见证数据（只为SegWit和Taproot设置）
    tx.witnesses = []  # 清空现有见证数据
    # tx.set_witness(0, TxWitnessInput([]))
    # tx.set_witness(1, TxWitnessInput([sig2, from_pub.to_hex()]))
    # tx.set_witness(2, TxWitnessInput([sig3]))
    tx.witnesses.append(TxWitnessInput([]))
    tx.witnesses.append(TxWitnessInput([sig2, from_pub.to_hex()]))
    tx.witnesses.append(TxWitnessInput([sig3]))
    
    print("tx:", tx)
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从 Legacy 地址: {legacy_address.to_string()}")
    print(f"从 SegWit 地址: {segwit_address.to_string()}")
    print(f"从 Taproot 地址: {taproot_address.to_string()}")
    print(f"总输入金额: {total_input/100000000} BTC")
    print(f"发送金额: {amount_to_send/100000000} BTC")
    print(f"手续费: {fee/100000000} BTC")
    
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")
    
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