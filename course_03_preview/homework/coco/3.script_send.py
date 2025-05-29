from btclib.script import ScriptPubKey, input_script_sig, Witness, serialize
from btclib.tx import TxIn, OutPoint, TxOut, Tx


script=['OP_1']
script=['OP_1','OP_1','OP_ADD', 2,'OP_EQUAL']

# 脚本树
script_tree = [(0xC0, script)]

# reveal地址
reveal_address = ScriptPubKey.p2tr(None, script_tree, network='mainnet').address

# reveal脚本,块控制
reveal_script, reveal_control = input_script_sig(None, script_tree, 0)

print(reveal_address,reveal_script,reveal_control.hex())

utxo={'txid': '7db63eb42991d96bf7da47ae368539b8a5569488e7dc1265bd324d60208dceb9', 'vout': 0,
                  'satoshi': 100000}



tx_in = [TxIn(OutPoint(utxo['txid'], utxo['vout']), sequence=0xfffffffd,
              script_witness=Witness([
                  serialize(script),
                  reveal_control.hex()
              ]))]
#   输出
tx_out = [TxOut(utxo['satoshi'],ScriptPubKey.from_address(reveal_address))]

tx = Tx(vin=tx_in, vout=tx_out)

print(tx.serialize(include_witness=True, check_validity=False).hex())
