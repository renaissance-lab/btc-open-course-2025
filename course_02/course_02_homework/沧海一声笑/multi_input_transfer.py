"""
从多个不同类型的地址（Legacy、SegWit、Taproot）构建一个交易
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress, P2trAddress
from bitcoinutils.script import Script

def main():
    # 设置测试网
    setup('regtest')
    
    # 创建私钥对象
    private_key = PrivateKey('cRN6iYkJookUYiBH32PWyaf1arRDGq6gDbw7QRi3R5b2nPJdnkuv')
    public_key = private_key.get_public_key()
    
    # 创建输入地址对象
    segwit_address = P2wpkhAddress('bcrt1qj5q6huak207m39d4g3x33asyywdph4ytqlawvn')
    legacy_address = P2pkhAddress('mu6pyndsCSKMgF8hgJbNVB55fqdnRbSu3E')
    taproot_address = P2trAddress('bcrt1ppa6nyqcg6pzl9563fl06p6pmjcg0ks8fs9yca0herc7akgpku2mqefvkt0')
    
    # 创建输出地址对象
    to_address = P2pkhAddress('moyxCWpvEg9w5gGGV3XVEGwQXttDdtoEkc')
    
    # 创建交易输入
    segwit_txin = TxInput(
        '469c218fd76cc6becce9aab38f0ff1eb4d7bed311267f9b106652768129aa6fa',
        0
    )
    
    legacy_txin = TxInput(
        '8dd41e28cfe4dc4479d82d5fb9a08550cc5983a9f1e3ab182c707385a9a5f7fe',
        0
    )
    
    taproot_txin = TxInput(
        'b23baee924d4e153a22f9cbe77f7a4efcd4e9ce84df130eb855f007bdb6605e9',
        0
    )
    
    # 输入金额
    segwit_amount = 1.56250000
    legacy_amount = 0.39062500
    taproot_amount = 0.78125000
    
    total_input = segwit_amount + legacy_amount + taproot_amount
    
    # 预估手续费 (假设每个输入需要 1000 聪)
    estimated_fee = 0.00003000  # 3个输入，每个1000聪
    
    # 计算输出金额
    output_amount = total_input - estimated_fee
    
    # 创建交易输出
    txout = TxOutput(
        to_satoshis(output_amount),
        to_address.to_script_pub_key()
    )
    
    # 创建交易（启用 segwit）
    tx = Transaction([segwit_txin, legacy_txin, taproot_txin], [txout], has_segwit=True)
    
    print("\n未签名的交易:")
    print(tx.serialize())
    print("\nTxId:", tx.get_txid())
    
    # 获取所有输入的脚本和金额
    segwit_script = segwit_address.to_script_pub_key()
    legacy_script = legacy_address.to_script_pub_key()
    taproot_script = taproot_address.to_script_pub_key()
    
    # 所有输入的脚本列表
    utxos_script_pubkeys = [segwit_script, legacy_script, taproot_script]
    
    # 所有输入的金额列表
    amounts = [
        to_satoshis(segwit_amount),
        to_satoshis(legacy_amount),
        to_satoshis(taproot_amount)
    ]
    
    # 签名 SegWit 输入
    # 对于 P2WPKH，我们需要使用 P2PKH 脚本作为 script_code
    segwit_script_code = Script([
        "OP_DUP",
        "OP_HASH160",
        public_key.get_address().to_hash160(),
        "OP_EQUALVERIFY",
        "OP_CHECKSIG"
    ])
    
    segwit_sig = private_key.sign_segwit_input(
        tx,
        0,
        segwit_script_code,  # 使用 P2PKH 脚本作为 script_code
        to_satoshis(segwit_amount)
    )
    
    # 签名 Legacy 输入
    legacy_sig = private_key.sign_input(tx, 1, legacy_script)
    legacy_pubkey = public_key.to_hex()
    
    # 签名 Taproot 输入
    taproot_sig = private_key.sign_taproot_input(
        tx,
        2,
        utxos_script_pubkeys,  # 传入所有输入的脚本
        amounts  # 传入所有输入的金额
    )
    
    # 设置 Legacy 输入的解锁脚本
    legacy_txin.script_sig = Script([legacy_sig, legacy_pubkey])
    
    # 添加见证数据
    tx.witnesses = []  # 清空见证列表
    tx.witnesses.append(TxWitnessInput([segwit_sig, public_key.to_hex()]))  # SegWit
    tx.witnesses.append(TxWitnessInput([]))  # Legacy (空见证)
    tx.witnesses.append(TxWitnessInput([taproot_sig]))  # Taproot
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n已签名的交易:")
    print(signed_tx)
    
    print("\n交易信息:")
    print(f"SegWit 输入金额: {segwit_amount} BTC")
    print(f"Legacy 输入金额: {legacy_amount} BTC")
    print(f"Taproot 输入金额: {taproot_amount} BTC")
    print(f"总输入金额: {total_input} BTC")
    print(f"手续费: {estimated_fee} BTC")
    print(f"输出金额: {output_amount} BTC")
    print(f"交易大小: {tx.get_size()} bytes")
    print(f"虚拟大小: {tx.get_vsize()} vbytes")
    print("\n您可以在这里广播交易:")
    print("https://mempool.space/testnet/tx/push")

if __name__ == "__main__":
    main() 