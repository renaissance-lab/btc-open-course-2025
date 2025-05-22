from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2wpkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.script import Script


def send_from_taproot_to_segwit(wif, txid, vout, amount_sat, send_amt, fee_sat, recipient_addr):
    setup('testnet')

    # 初始化密钥和地址
    priv = PrivateKey.from_wif(wif)
    pub = priv.get_public_key()
    sender_addr = pub.get_taproot_address()
    from_script = sender_addr.to_script_pub_key()  
    scripts = [from_script]
    print(scripts)
    # 创建输入
    txin = TxInput(txid, vout)

    # 创建输出脚本：SegWit 地址
    to_script = P2wpkhAddress(recipient_addr).to_script_pub_key()

    # 简单手续费估算

    txout = TxOutput(send_amt, to_script)

    # 创建交易并签名（Taproot 简化版本，不涉及 script-path 花费）
    tx = Transaction([txin], [txout], has_segwit=True)
    sig = priv.sign_taproot_input(
        tx, 
        0,
        scripts,
        [amount_sat]
    )
    # 添加 Taproot witness 数据（仅 key-path）
    tx.witnesses = [TxWitnessInput([sig])]

    # 输出交易原始 hex
    print("Raw signed tx:", tx.serialize())
    return tx.serialize()

send_from_taproot_to_segwit(
    wif='cSqDDxiKf5PbFoVTLZmYeuM73AE84tuofLvjRi7SnSW5F7571MK9',
    txid='a421caba4fbf0f70d51a1712ef16b4fdf25dd0dd7c6f60979b8df8060548b566',
    vout=0,
    amount_sat=1000,
    send_amt=600,
    fee_sat=250,
    recipient_addr='tb1q6e80ydwcmdm6fqs4fss4jezd2xlgp5r2ng8c02'
)