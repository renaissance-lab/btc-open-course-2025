import math

import requests
from btclib.ecc import libsecp256k1
from btclib.script import ScriptPubKey, Witness, sig_hash
from btclib.tx import TxIn, OutPoint, TxOut, Tx
from btclib.amount import sats_from_btc

def get_utxos(address):
    url = f"https://open-api.unisat.io/v1/indexer/address/{address}/utxo-data?cursor=0&size=1000"

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
        "Connection": "keep-alive",
        "Authorization": "Bearer d07c3a32bbc3b80a7de6eb60b1dd9253ee6e6afe2b6941c4a1943c2ef9266dac"
    }

    try:

        response = requests.get(url, headers=headers)
        utxos = response.json()['data']['utxo']
        keys_to_keep = ['txid', 'vout', 'satoshi']

        filtered_data = [
            {key: item[key] for key in keys_to_keep if key in item}
            for item in utxos
            if item.get('satoshi', 0) >= 600
        ]

        return filtered_data
    except requests.RequestException as e:
        print(f"Error fetching UTXOs: {e}")
        return []

def send_btc(amount, address,fee):
    funds_wallet = {'mnemonic': 'swear debate liberty debate float always hover dragon sunset uncover certain foil', 'Wif': 'L5TGMyc9rNsMn5EJcoM9Y9p8fDPSoE8szeSKzgvpQ1KvR3SppgL6', 'private_key': 'f5ac19f197983e51cba1b85e41eea05b91d229c93169ff122604a3c0583138f0', 'public_key': '024fac82e4933443a744896aa8d5714be4694b9fdab7d461a350444b64bc5fc589', 'address': 'bc1qns2l66lq9d99c9w2vyk8yhmwh94kjagwcm4w7d'}


    utxos=get_utxos(funds_wallet['address'])

    tx_in = []
    prevouts = []
    sum_vin_value = 0
    tx_out = []

    for utxo in utxos:
        tx_in.append(TxIn(OutPoint(utxo['txid'], utxo['vout']), sequence=0xfffffffd, script_witness=Witness([
            '0' * 142,  # 签名
            funds_wallet['public_key']  # 公钥
        ])))
        sum_vin_value += utxo['satoshi']
        prevouts.append(TxOut(utxo['satoshi'], ScriptPubKey.from_address(funds_wallet['address'])))





    tx_out.append(TxOut(sats_from_btc(amount),
                        ScriptPubKey.from_address(address)))
    tx_out.append(TxOut(sum_vin_value-amount,
                        ScriptPubKey.from_address(funds_wallet['address'])))


    tx = Tx(vin=tx_in, vout=tx_out)

    tx.vout[-1].value -= math.ceil(tx.vsize * fee)

    for i in range(len(utxos)):
        sig_hash_0 = sig_hash.from_tx(prevouts, tx, i, sig_hash.ALL)

        # 生成签名
        sig_0 = libsecp256k1.ecdsa_sign_(sig_hash_0, funds_wallet['private_key'])

        # 更新解锁脚本
        tx_in[i].script_witness.stack[0] = sig_0.hex() + '0' + str(sig_hash.ALL)


    tx_hex=tx.serialize(include_witness=True, check_validity=False).hex()
    return tx_hex

if __name__ == '__main__':

    send_btc(0.0001,'bc1qayp26zt6ke4tnluvdark74pkarard35vm9tkm9')








