# 多种输入类型（legacy、segwit、taproot）到legacy地址的转账代码
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.script import Script

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
    to_address = P2pkhAddress('mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1')
    
    # 显示各种地址信息
    print("\n=== 地址信息 ===")
    print(f"私钥 WIF: {from_private_key.to_wif()}")
    print(f"Legacy 地址: {legacy_address.to_string()}")
    print(f"SegWit 地址: {segwit_address.to_string()}")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    print(f"目标 Legacy 地址: {to_address.to_string()}")
    
    
    legacy_amount = to_satoshis(0.00014800)
    segwit_amount = to_satoshis(0.00014800)
    taproot_amount = to_satoshis(0.00001)
    
    # 计算总输入金额
    total_input = legacy_amount + segwit_amount + taproot_amount
    
    # 设置手续费
    fee = to_satoshis(0.000004)  # 0.000004 BTC
    # fee = to_satoshis(estimate_fee())
    
    # 计算发送金额
    amount_to_send = total_input - fee

    # 创建多个交易输入
    txin_legacy = TxInput(
        '9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be',
        0
    )
    
    txin_segwit = TxInput(
        '9074b92dfd270ba4eb928bb7ea03ce69a80ef538bd3d354761411b4aa35c91be',
        1
    )
    
    txin_taproot = TxInput(
        '1a338c80a5be61258ea4e5b5f1ce2d213c22fa340afdd1999a90135e775022bb',
        0
    )
    txinputs = [txin_legacy, txin_segwit, txin_taproot]

    # 创建交易输出
    txout = TxOutput(amount_to_send, to_address.to_script_pub_key())
    
    # 创建交易
    tx = Transaction(txinputs, [txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    
    # 准备所有脚本和金额数组（按照新脚本方式）
    legacy_script = legacy_address.to_script_pub_key()
    # 从公钥派生脚本，因为地址是segwit地址
    segwit_script = from_pub.get_address().to_script_pub_key()
    taproot_script = taproot_address.to_script_pub_key()
    utxos_script_pubkeys = [legacy_script, segwit_script, taproot_script]
    amounts = [legacy_amount, segwit_amount, taproot_amount]
    
    # 签名所有输入
    sig1 = from_private_key.sign_input(tx, 0, legacy_script)
    sig2 = from_private_key.sign_segwit_input(tx, 1, segwit_script, amounts[1])
    # sig3 = from_private_key.sign_taproot_input(tx, 2, [taproot_script], [taproot_amount])
    sig3 = from_private_key.sign_taproot_input(tx, 2, utxos_script_pubkeys, amounts)
    
    # Legacy输入使用script_sig
    txinputs[0].script_sig = Script([sig1, from_pub.to_hex()])
    
    # SegWit输入使用空script_sig和witness
    txinputs[1].script_sig = Script([])
    # txinputs[2].script_sig = Script([])
    
    # 设置见证数据（只为SegWit和Taproot设置）
    tx.witnesses = []  # 清空现有见证数据
    tx.set_witness(1, TxWitnessInput([sig2, from_pub.to_hex()]))
    tx.set_witness(2, TxWitnessInput([sig3]))
    
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"从 Legacy 地址: {legacy_address.to_string()}")
    print(f"从 SegWit 地址: {segwit_address.to_string()}")
    print(f"从 Taproot 地址: {taproot_address.to_string()}")
    print(f"到 Legacy 地址: {to_address.to_string()}")
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