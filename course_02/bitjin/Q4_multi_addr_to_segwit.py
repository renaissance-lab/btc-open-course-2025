from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2wpkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.script import Script

def estimate_fee(num_inputs, num_outputs, fee_rate=2):
    # 估算字节数（大致）：legacy:148, segwit:68, taproot:58
    # 这里只做简单估算，实际应更精确
    return (148*num_inputs + 34*num_outputs + 10) * fee_rate

def send_utxo_to_segwit(utxo, send_amount, recipient_addr, fee_rate=2):
    setup('testnet')
    priv = PrivateKey.from_wif(utxo['wif'])
    addr_type = utxo['address_type']
    amount = utxo['amount']

    # 选择输入脚本类型
    if addr_type == 'legacy':
        sender_addr = priv.get_public_key().get_address()
        from_script = sender_addr.to_script_pub_key()
        scripts = [from_script]
    elif addr_type == 'segwit':
        sender_addr = priv.get_public_key().get_segwit_address()
        from_script = sender_addr.to_script_pub_key()
        scripts = [from_script]
    elif addr_type == 'taproot':
        sender_addr = priv.get_public_key().get_taproot_address()
        from_script = sender_addr.to_script_pub_key()
        scripts = [from_script]
    else:
        raise Exception('Unknown address type')

    txin = TxInput(utxo['txid'], utxo['vout'])
    to_script = P2wpkhAddress(recipient_addr).to_script_pub_key()

    # 预估手续费
    fee = estimate_fee(1, 1, fee_rate)
    send_amt = send_amount - fee
    if send_amt <= 0:
        raise Exception('Amount too small after fee')

    txout = TxOutput(send_amt, to_script)
    tx = Transaction([txin], [txout], has_segwit=True)

    # 签名
    if addr_type == 'legacy':
        sig = priv.sign_input(tx, 0, from_script, amount) + b'\x01'  # 加SIGHASH_ALL
        tx.inputs[0].script_sig = Script([sig, priv.get_public_key().to_hex()])
    elif addr_type == 'segwit':
        sig = priv.sign_segwit_input(tx, 0, from_script, amount)
        tx.witnesses = [TxWitnessInput([sig, priv.get_public_key().to_hex()])]
    elif addr_type == 'taproot':
        sig = priv.sign_taproot_input(tx, 0, scripts, [amount])
        tx.witnesses = [TxWitnessInput([sig])]
    else:
        raise Exception('Unknown address type')

    print("Raw signed tx:", tx.serialize())
    return tx.serialize()

##ex
utxo = {
    'txid': 'd09f60cff5fff5017afab3bfbac1c4536712cbd56d7d1beb3b4d03f7863adf25',
    'vout': 1,
    'amount': 1000,  # 单位：satoshi
    'address_type': 'segwit',  # 'legacy' | 'segwit' | 'taproot'
    'wif': 'cV7uxejE12LRqVUJmoqdoigKncN3BxbrJrDWjraPmeQXQs8tPkyg'
}
recipient_addr = 'tb1q97taqahnh4akf69jazqu57p5h7gypfmm5ktare'  # 目标 segwit 地址
send_utxo_to_segwit(utxo, 800, recipient_addr, fee_rate=1)