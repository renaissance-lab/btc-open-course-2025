#segwit address
# Private key (WIF): cV7uxejE12LRqVUJmoqdoigKncN3BxbrJrDWjraPmeQXQs8tPkyg
# Public key: 0374b0ed05bdf3b2ab35a18d2b9f2224c2483261d7b04f69891dd65560786dc63a
# P2WPKH SegWit Address: tb1q6e80ydwcmdm6fqs4fss4jezd2xlgp5r2ng8c02


from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.script import Script
from bitcoinutils.utils import to_satoshis
from bitcoinutils.constants import SIGHASH_ALL


# Configure for Bitcoin testnet
setup('testnet')

# 1. Sender's private key (WIF) and derived addresses
sender_wif = 'cV7uxejE12LRqVUJmoqdoigKncN3BxbrJrDWjraPmeQXQs8tPkyg'
priv = PrivateKey.from_wif(sender_wif)
pub = priv.get_public_key()
sender_address = pub.get_segwit_address()  # native SegWit (bech32) address
print("Sender SegWit address:", sender_address)


# 2. Define the UTXO to spend (replace placeholders with actual values)
txid = 'd09f60cff5fff5017afab3bfbac1c4536712cbd56d7d1beb3b4d03f7863adf25'   # e.g. 'abcd1234...'
vout = 1                  # the output index of the UTXO, must be an integer
input_amount = 0.00001200          # the amount of the UTXO in BTC (example)

# 3. Define recipient (legacy P2PKH) and change addresses
recipient_addr = P2pkhAddress('mp5ZdLCfdoPpCJvQNaqTkjaSkctjw7E4n9')  # Legacy address
change_addr = sender_address  # change back to sender (P2WPKH)

# 4. Compute amounts: fee and outputs
fee = 0.00000300  #  BTC transaction fee (example)
send_amount = input_amount - fee  # send the rest to recipient
change_amount = input_amount - send_amount - fee  # leftover as change (likely 0 here)
send_satoshis = to_satoshis(send_amount)
change_satoshis = to_satoshis(change_amount)

# 5. Create transaction inputs/outputs
txin = TxInput(txid, vout)
txout_recipient = TxOutput(send_satoshis, recipient_addr.to_script_pub_key())
txout_change = TxOutput(change_satoshis, change_addr.to_script_pub_key())

# If change_amount is zero, you can omit txout_change from the outputs list
outputs = [txout_recipient]
if change_satoshis > 0:
    outputs.append(txout_change)

# 6. Build transaction; mark it has segwit
tx = Transaction([txin], outputs, has_segwit=True)

# 7. Create script code for signing (P2PKH script)
pubkey_hash = pub.get_address().to_hash160()
script_code = Script(['OP_DUP', 'OP_HASH160', pubkey_hash, 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

# 8. Sign the segwit input (index 0)
sig = priv.sign_segwit_input(tx, 0, script_code, to_satoshis(input_amount), SIGHASH_ALL)

# 9. Attach witness (signature + pubkey)
tx.witnesses.append(TxWitnessInput([sig, pub.to_hex()]))  # 使用 TxWitnessInput 包装见证数据

# 10. Serialize and print raw transaction hex
raw_tx_hex = tx.serialize()
print("Raw signed transaction (hex):", raw_tx_hex)