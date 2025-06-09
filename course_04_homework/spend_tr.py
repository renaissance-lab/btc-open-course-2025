from bitcoinutils.keys import P2pkhAddress, PrivateKey,PublicKey,P2trAddress
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.schnorr import schnorr_verify
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput, Sequence

from btc_util import get_pk_from_priv_wif, get_script_pub_key,gen_send_btc_tx,get_utxos_script_pubkeys,get_balance_from_utxo
from btc_info_request import post_tx
from gen_leaf import get_x_only_hex_pk_from_priv_wif, get_script_path_addr,gen_all_leafs,gen_hash_script,buildTimelockScript,gen_multi_sign_leaf,TIME_LOCK
from config import *


def send_btc():
    priv = PrivateKey(btc_wif5)
    from_addr = btc_addr5

    tr_address = get_script_path_addr()
    to_addr = tr_address.to_string()
    amount = 8200

    tx,txin_amount_list = gen_send_btc_tx(from_addr, to_addr, amount, chain_name="testnet")
    utxos_script_pubkeys = get_utxos_script_pubkeys(from_addr,len(tx.inputs))

    for txin_index in range(len(tx.inputs)):
        sig = priv.sign_taproot_input(tx, txin_index, utxos_script_pubkeys, txin_amount_list)
        tx.witnesses.append(TxWitnessInput([sig]))
    return tx.serialize()

# tx sample
# https://mempool.space/testnet/tx/e562d607daa1c027650d706a3f7b64ae382f47fdbc658fa3549779079727dc35
def spend_key_path():
    to_addr = btc_addr5
    amount = 2200

    priv = PrivateKey(btc_wif2)

    internal_pub = PublicKey(btc_pubkey2)
    all_leafs = gen_all_leafs()
    tr_address = internal_pub.get_taproot_address(all_leafs)
    from_addr = tr_address.to_string()
    is_odd = tr_address.is_odd()

    tx,txin_amount_list = gen_send_btc_tx(from_addr, to_addr, amount, chain_name="testnet")
    utxos_script_pubkeys = get_utxos_script_pubkeys(from_addr,len(tx.inputs))

    for txin_index in range(len(tx.inputs)):
        sig = priv.sign_taproot_input(tx, txin_index, utxos_script_pubkeys, txin_amount_list, tapleaf_scripts=all_leafs)

        print("len((tr_address.to_witness_program()):",len(tr_address.to_witness_program()))
        verify_result = schnorr_verify(bytes.fromhex(tx.get_txid()), bytes.fromhex(tr_address.to_witness_program()), bytes.fromhex(sig))
        print("verify_result:",verify_result)

        tx.witnesses.append(TxWitnessInput([sig]))
    return  tx.serialize()

# tx sample: 
# https://mempool.space/testnet/tx/d0fe10dff947f594b2aba39a4da7f3d622e4ec7beaa0595eddf8294b9babaf01
def spend_hash_leaf():
    to_addr = btc_addr5
    amount = 2100

    priv = PrivateKey(btc_wif1)

    internal_pub = PublicKey(btc_pubkey2)
    all_leafs = gen_all_leafs()
    tr_address = internal_pub.get_taproot_address(all_leafs)
    from_addr = tr_address.to_string()
    is_odd = tr_address.is_odd()

    hash_script = gen_hash_script()

    control_block = ControlBlock(internal_pub, scripts=all_leafs, index=0, is_odd=is_odd)
    tx,txin_amount_list = gen_send_btc_tx(from_addr, to_addr, amount, chain_name="testnet")    
    tx.witnesses.append(TxWitnessInput([b"good".hex(), hash_script.to_hex(), control_block.to_hex()]))
    return  tx.serialize()

# https://mempool.space/testnet/tx/a637850b197f4d691c51cf12265ebba2b52808c8841a31a9ceddf204e884b2fb
def spend_time_lock_leaf():
    to_addr = btc_addr5
    amount = 900

    priv = PrivateKey(btc_wif2)

    internal_pub = PublicKey(btc_pubkey2)
    all_leafs = gen_all_leafs()
    tr_address = internal_pub.get_taproot_address(all_leafs)
    from_addr = tr_address.to_string()
    is_odd = tr_address.is_odd()
    print(f"from_addr:{from_addr}")

    time_lock_script = buildTimelockScript()
    control_block = ControlBlock(internal_pub, scripts=all_leafs, index=2, is_odd=is_odd)

    sequence = Sequence(TYPE_RELATIVE_TIMELOCK, TIME_LOCK).for_input_sequence()
    # sequence=sequence, 
    print("sequence:",sequence)
    tx,txin_amount_list = gen_send_btc_tx(from_addr, to_addr, amount, sequence=sequence, chain_name="testnet")    
    utxos_script_pubkeys = get_utxos_script_pubkeys(from_addr,len(tx.inputs))

    for txin_index in range(len(tx.inputs)):
        sig = priv.sign_taproot_input(
                tx,
                txin_index,
                utxos_script_pubkeys,
                txin_amount_list,
                script_path=True,
                tapleaf_script=time_lock_script,
                tweak=False,
            )
        tx.witnesses.append(TxWitnessInput([sig, time_lock_script.to_hex(), control_block.to_hex()]))
    return  tx.serialize()

# https://mempool.space/testnet/tx/e7872a6e898ab9a74b6ad9a3cf7bfa081bf0c5beacdffb49162ccf2abc385499
def spend_multi_sign_leaf():
    to_addr = btc_addr5
    amount = 2600

    internal_pub = PublicKey(btc_pubkey2)
    all_leafs = gen_all_leafs()
    tr_address = internal_pub.get_taproot_address(all_leafs)
    from_addr = tr_address.to_string()
    is_odd = tr_address.is_odd()
    print(f"from_addr:{from_addr}")

    multi_sign_leaf = gen_multi_sign_leaf()
    print("multi_sign_leaf: ",multi_sign_leaf)
    control_block = ControlBlock(internal_pub, scripts=all_leafs, index=1, is_odd=is_odd)

    tx,txin_amount_list = gen_send_btc_tx(from_addr, to_addr, amount, chain_name="testnet")    
    utxos_script_pubkeys = get_utxos_script_pubkeys(from_addr,len(tx.inputs))
    print("before tx.get_txid():",tx.get_txid())

    for txin_index in range(len(tx.inputs)):
        sig2 = PrivateKey(btc_wif2).sign_taproot_input(
                tx,
                txin_index,
                utxos_script_pubkeys,
                txin_amount_list,
                script_path=True,
                tapleaf_script=multi_sign_leaf,
                tweak=False,
            )
        print("sig2:",sig2)
        # print("len(bytes.fromhex(sig2)):",len(bytes.fromhex(sig2)))
        # print("PrivateKey(btc_wif2).get_public_key().to_hex():," , PrivateKey(btc_wif2).get_public_key().to_x_only_hex())

        # verify_result = schnorr_verify(bytes.fromhex(tx.get_txid()),  bytes.fromhex(PrivateKey(btc_wif2).get_public_key().to_x_only_hex()), bytes.fromhex(sig2))
        # print("verify_result:",verify_result)

        # sig3 = PrivateKey(btc_wif3).sign_taproot_input(
        #         tx,
        #         txin_index,
        #         utxos_script_pubkeys,
        #         txin_amount_list,
        #         script_path=True,
        #         tapleaf_script=multi_sign_leaf,
        #         tweak=False,
        #     )
        sig4 = PrivateKey(btc_wif4).sign_taproot_input(
                tx,
                txin_index,
                utxos_script_pubkeys,
                txin_amount_list,
                script_path=True,
                tapleaf_script=multi_sign_leaf,
                tweak=False,
            )
        tx.witnesses.append(TxWitnessInput([sig4, "", sig2, multi_sign_leaf.to_hex(), control_block.to_hex()]))

    print("tx:",tx)
    print("tx.get_txid():",tx.get_txid())
    return  tx.serialize()

# target addr sample: tb1pruw4z3rdazp9yyn7g7fw6czkyg3j9g2l3f5d0pwcul03vchww0vq5dfnjk
if __name__ == "__main__":
    setup("testnet")    

    tr_address = get_script_path_addr()
    addr = tr_address.to_string()
    # is_odd = tr_address.is_odd()
    # print(f"addr:{addr}, is_odd:{is_odd}")

    balance = get_balance_from_utxo(addr,chain_name="testnet")
    print(f"balance:{balance}")

    # raw_data = send_btc()
    raw_data = spend_key_path()
    # raw_data = spend_hash_leaf()
    # raw_data = spend_time_lock_leaf()
    # raw_data = spend_multi_sign_leaf()

    # # post_result = post_tx(raw_data)
    # print("post_result:",post_result)

    







    






