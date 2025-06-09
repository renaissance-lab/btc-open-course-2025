
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import P2pkhAddress, PrivateKey, P2trAddress, P2wpkhAddress,P2wshAddress,P2shAddress,PublicKey
from bitcoinutils.setup import setup

from btc_info_request import request_fee_rate, request_utxo


# setup("mainnet")

def get_taproot_addr_from_pubkey(pubkey):
    internal_pub = PublicKey(pubkey)
    taproot_address = internal_pub.get_taproot_address()
    addr = taproot_address.to_string()
    is_odd = taproot_address.is_odd()
    return addr, is_odd

def get_x_only_hex_pk_from_priv_wif(priv_wif):
    priv = PrivateKey(priv_wif)
    pub = priv.get_public_key()
    return pub.to_x_only_hex()

def get_pk_from_priv_wif(priv_wif):
    priv = PrivateKey(priv_wif)
    pub = priv.get_public_key()
    return pub.to_hex()

def get_taproot_addr_from_priv_wif(priv_wif):
    priv = PrivateKey(priv_wif)
    pub = priv.get_public_key()
    fromAddress = pub.get_taproot_address()
    return fromAddress.to_string()

def get_txin_list(tx_info_list,sequence="ffffffff"):
    txin_list = []
    txin_amount_list = []
    txin_amount_sum = 0
    for tx_info in tx_info_list:
        txid = tx_info["txid"]
        vout = tx_info["vout"]
        txin = TxInput(txid, vout,sequence=sequence)
        txin_list.append(txin)

        pre_amount = tx_info["value"]
        txin_amount_list.append(pre_amount)
        txin_amount_sum = txin_amount_sum + pre_amount

    return txin_list,txin_amount_list,txin_amount_sum

# Fee（聪） = Transaction vSize（vB） × FeeRate（sats/vB）
# Taproot 输入	~60 vB
# Taproot 输出	~43 vB
def get_fee_btc(in_count=1,out_count=2):
    if in_count > 10:
        raise Exception(f"in_count:{in_count} > 10.")
    v_size = 10 + in_count*60 + out_count*43 

    fee_rate = int(request_fee_rate())
    if fee_rate > 20:
        raise Exception(f"btc_fee_rate:{fee_rate} > 20.")
    
    MAX_BTC_MINER_FEE = int(0.0001 * 10**8)
    fee = int(v_size*fee_rate)
    if fee > MAX_BTC_MINER_FEE:
        raise Exception(f"btc_fee:{fee} > {MAX_BTC_MINER_FEE}, btc_fee is too big.")

    return fee

def get_utxo_info(addr,chain_name="bitcoin"):
    utxo_info_list = []

    utxo_list =  request_utxo(addr,chain_name)
    # print(f"utxo_list: {utxo_list} , addr: {addr}")
    for utxo in utxo_list:
        if utxo["status"]["confirmed"] == True:
            utxo_info = {
                    "txid": utxo["txid"],
                    "vout": utxo["vout"],
                    "value": utxo["value"]
                }
            utxo_info_list.append(utxo_info)

    return utxo_info_list

def get_balance_from_utxo(addr,chain_name="bitcoin"):
    utxo_info_list = []
    balance = 0

    utxo_list =  request_utxo(addr,chain_name)
    for utxo in utxo_list:
        if utxo["status"]["confirmed"] == True:
            balance += utxo["value"]

    return balance

def get_txOut(target_addr, amount):
    return TxOutput(amount, get_script_pub_key(target_addr))

def get_script_pub_key(addr):
    if addr.startswith("bc1p") or addr.startswith("tb1p"):
        return P2trAddress(addr).to_script_pub_key()
    elif addr.startswith("bc1q") or addr.startswith("tb1q"):
        return P2wpkhAddress(addr).to_script_pub_key()
    elif addr.startswith("1") or addr.startswith("m") or addr.startswith("n"):
        return P2pkhAddress(addr).to_script_pub_key()
    # elif addr.startswith("3") or addr.startswith("2"):
    #     return P2shAddress(addr).to_script_pub_key()
    #     return P2wshAddress(addr).to_script_pub_key()
    else: 
        raise Exception(f"address:{addr}, unsupported address prefix")

def is_bitcoin_mainnet_addr(addr):
    if addr.startswith("bc1p") or addr.startswith("bc1q") or addr.startswith("1") or addr.startswith("3"):
        return True
    elif addr.startswith("tb1p") or addr.startswith("tb1q") or addr.startswith("m") or addr.startswith("n") or addr.startswith("2"):
        return False
    else:
        raise Exception(f"address:{addr}, unsupported address prefix")

def get_utxos_script_pubkeys(from_addr, tx_len):
    first_script_pubkey = get_script_pub_key(from_addr)
    utxos_script_pubkeys = []
    for i in range(tx_len):
        utxos_script_pubkeys.append(first_script_pubkey)
    return utxos_script_pubkeys

def gen_send_btc_tx(from_addr, to_addr, to_amount, sequence="ffffffff", chain_name="bitcoin"):
    utxo_info_list = get_utxo_info(from_addr, chain_name=chain_name)
    txin_list,txin_amount_list,txin_amount_sum = get_txin_list(utxo_info_list,sequence=sequence)
    
    btc_fee = get_fee_btc(len(txin_list))
    if txin_amount_sum == 0:
        raise Exception(f"from_addr:{from_addr}, txin_amount_sum == 0, utxo_info_list:{utxo_info_list}")
    elif to_amount < 0:
        raise Exception(f"to_amount error, to_amount:{to_amount} < 0.")
    elif to_amount == 0:
        if txin_amount_sum < btc_fee:
            raise Exception(f"txin_amount_sum is too small, txin_amount_sum:{txin_amount_sum} < btc_fee:{btc_fee}.")
        to_amount = txin_amount_sum - btc_fee
        to_txOut = get_txOut(to_addr,to_amount)
        txOut_list = [to_txOut]
    elif txin_amount_sum < to_amount:
        raise Exception(f"to_amount is too big, txin_amount_sum:{txin_amount_sum} < to_amount:{to_amount}.")
    elif (txin_amount_sum-to_amount < btc_fee):
        raise Exception(f"btc_fee is not enough, txin_amount_sum-to_amount:{txin_amount_sum-to_amount} < btc_fee:{btc_fee}.")
    else:
        return_amount = txin_amount_sum - to_amount - btc_fee
        return_txOut = get_txOut(from_addr,return_amount)
        to_txOut = get_txOut(to_addr,to_amount)
        txOut_list = [to_txOut,return_txOut]
    
    tx = Transaction(txin_list, txOut_list, has_segwit=True)
    return tx,txin_amount_list

def gen_addr_by_script_path_and_addr(internal_addr, tapleaf_scripts):
    internal_pub = P2trAddress(internal_addr).to_script_pub_key()
    return internal_pub.get_taproot_address(tapleaf_scripts).to_string()

def gen_addr_by_script_path_and_priv(internal_priv, tapleaf_scripts):
    privkey_tr_script = PrivateKey(internal_priv)
    internal_pub = internal_priv.get_public_key()
    return internal_pub.get_taproot_address(tapleaf_scripts).to_string()



