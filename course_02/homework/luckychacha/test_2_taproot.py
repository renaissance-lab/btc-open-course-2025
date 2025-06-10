# 多种输入类型（legacy、segwit、taproot）到legacy地址的转账代码
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2wpkhAddress, P2trAddress
from bitcoinutils.script import Script

from utils import BitcoinAddressInfo

def main():
    # 设置测试网
    setup('testnet')
    
    # 私钥
    from_private_key = PrivateKey('cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh')
    from_pub = from_private_key.get_public_key()

    from_private_key2 = PrivateKey('cPRZu2gevUDWnnukiiXUf7C6MTx3HSbnhex6YbmtAwXF9b4qePxr')
    from_pub2 = from_private_key2.get_public_key()
    
    util = BitcoinAddressInfo()
    
    taproot_address = from_pub.get_taproot_address()
    taproot_address_utxos = util.get_address_utxos(taproot_address.to_string())
    taproot_amount = 0
    taproot_address_vout = 0
    taproot_address_txid = ''
    for utxo in taproot_address_utxos:
        taproot_amount += to_satoshis(utxo['value'])
        taproot_address_vout = utxo['vout']
        taproot_address_txid = utxo['txid']
        print("address1 utxo:", utxo)
        break

    taproot_address2 = from_pub2.get_taproot_address()
    taproot_address2_utxos = util.get_address_utxos(taproot_address2.to_string())
    taproot_amount2 = 0
    taproot_address2_vout = 0
    taproot_address2_txid = ''
    for utxo in taproot_address2_utxos:
        taproot_amount2 += to_satoshis(utxo['value'])
        taproot_address2_vout = utxo['vout']
        taproot_address2_txid = utxo['txid']
        print("address2 utxo:", utxo)
        break

    if taproot_amount == 0 or taproot_amount2 == 0:
        print("没有足够的UTXO")
        return
    # 接收方地址（Taproot）
    to_address = P2trAddress('tb1pwzpfp6auj4v9c46n8pyf8d9ul70avxcwq7wl8x8z5kdt9983nmqsw8cpxp')
    to_address2 = P2wpkhAddress('tb1qq2x3nt3zzqz7rxgxf03m4tj5eckywehaklggph')
    # 显示各种地址信息
    print("\n=== 地址信息 ===")
    print(f"私钥 WIF: {from_private_key.to_wif()}")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"Taproot 地址2: {taproot_address2.to_string()}")
    print(f"目标 Taproot 地址: {to_address.to_string()}")
    
    
    # taproot_amount = to_satoshis(0.00001000)
    # taproot_amount2 = to_satoshis(0.0001)
    # 计算总输入金额
    total_input = taproot_amount + taproot_amount2
    
    # 设置手续费
    fee = to_satoshis(0.000004)  # 0.000004 BTC
    # fee = to_satoshis(estimate_fee())
    
    # 计算发送金额
    amount_to_send = total_input - fee
# 02000000000102bb2250775e13909a99d1fd0a34fa223c212dcef1b5e5a48e2561bea5808c331a0000000000fdffffffb9e73d39d6c5ee2327b40b401e078fa0d702f986026803615a5572058fd884e70000000000fdffffff016829000000000000225120708290ebbc95585c5753384893b4bcff9fd61b0e079df398e2a59ab294f19ec10140f1c066309d4bba694c76f32144a89f19f7fe787c86f7308f4b877082e8c187b8446272fa06671eba097283aa794e3e3b4502c0ce97f73bd12c5eb3354bf4f1ed0140b2fd0710129463517c5663a94de7667d1b05d68b2d5519a8f4a3f86b6256f0060a4e7bb0d0c552e732640a54070f9ac74d4f5b7db888522af88a51ca398c272400000000
# 02000000000102bb2250775e13909a99d1fd0a34fa223c212dcef1b5e5a48e2561bea5808c331a0000000000fdffffffb9e73d39d6c5ee2327b40b401e078fa0d702f986026803615a5572058fd884e70000000000fdffffff016829000000000000225120708290ebbc95585c5753384893b4bcff9fd61b0e079df398e2a59ab294f19ec10140f1c066309d4bba694c76f32144a89f19f7fe787c86f7308f4b877082e8c187b8446272fa06671eba097283aa794e3e3b4502c0ce97f73bd12c5eb3354bf4f1ed0140b2fd0710129463517c5663a94de7667d1b05d68b2d5519a8f4a3f86b6256f0060a4e7bb0d0c552e732640a54070f9ac74d4f5b7db888522af88a51ca398c272400000000
    # 创建多个交易输入
    
    txin_taproot = TxInput(taproot_address_txid,taproot_address_vout)
    txin_taproot2 = TxInput(taproot_address2_txid,taproot_address2_vout)
    txinputs = [txin_taproot, txin_taproot2]

    # 创建交易输出
    print("amount_to_send:", amount_to_send/2)
    txout = TxOutput(int(amount_to_send/2), to_address.to_script_pub_key())
    txout2 = TxOutput(int(amount_to_send/2), to_address2.to_script_pub_key())
    # 创建交易
    tx = Transaction(txinputs, [txout, txout2], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 准备所有脚本和金额数组（按照新脚本方式）
    taproot_script = taproot_address.to_script_pub_key()
    taproot_script2 = taproot_address2.to_script_pub_key()
    utxos_script_pubkeys = [taproot_script, taproot_script2]
    amounts = [taproot_amount, taproot_amount2]
    
    # 签名所有输入
    sig1 = from_private_key.sign_taproot_input(tx, 0, utxos_script_pubkeys, amounts)
    sig2 = from_private_key2.sign_taproot_input(tx, 1, utxos_script_pubkeys, amounts)
    
    
    txinputs[0].script_sig = Script([])

    txinputs[1].script_sig = Script([])
    # txinputs[0].script_sig = Script([])
    
    # 设置见证数据（只为SegWit和Taproot设置）
    tx.witnesses = []  # 清空现有见证数据
    tx.witnesses.append(TxWitnessInput([sig1]))
    tx.witnesses.append(TxWitnessInput([sig2]))

    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从 Taproot 地址: {taproot_address.to_string()}")
    print(f"从 Taproot 地址2: {taproot_address2.to_string()}")
    print(f"到 Taproot 地址: {to_address.to_string()}")
    print(f"总输入金额: {total_input/100000000} BTC")
    print(f"发送金额: {amount_to_send/100000000} BTC")
    print(f"手续费: {fee/100000000} BTC")
    
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")
    
    return signed_tx


def estimate_fee(fee_rate=10):
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

if __name__ == "__main__":
    main()