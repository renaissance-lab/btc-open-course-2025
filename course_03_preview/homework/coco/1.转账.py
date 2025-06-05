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


def send_btc(amount, address, fee):
    funds_wallet = {'mnemonic': 'burst urge coast trigger tired veteran blade era assume wonder industry settle',
                    'Wif': 'KznoQsBZ2sd1eC3Sd4C1KzUnFmNqgZUfukFKKbUmdufnyUCAVbTi',
                    'private_key': '6a88f64000a85589a40d0757df45188363456c0b060594c02c916bd4decd8b78',
                    'public_key': '02b414dcf4bb00637e73423f61897364422115cd91da00f4af12c21417d96f961c',
                    'address': 'bc1qxw78k4pqfvhljma6dkfr9j5hnnn2gc0xzll4wr'}

    utxos = get_utxos(funds_wallet['address'])

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
    tx_out.append(TxOut(sum_vin_value - amount,
                        ScriptPubKey.from_address(funds_wallet['address'])))

    tx = Tx(vin=tx_in, vout=tx_out)

    tx.vout[-1].value -= math.ceil(tx.vsize * fee)

    for i in range(len(utxos)):
        sig_hash_0 = sig_hash.from_tx(prevouts, tx, i, sig_hash.ALL)

        # 生成签名
        sig_0 = libsecp256k1.ecdsa_sign_(sig_hash_0, funds_wallet['private_key'])

        # 更新解锁脚本
        tx_in[i].script_witness.stack[0] = sig_0.hex() + '0' + str(sig_hash.ALL)

    tx_hex = tx.serialize(include_witness=True, check_validity=False).hex()
    return tx_hex


if __name__ == '__main__':
    send_btc(0.1, 'bc1qxw78k4pqfvhljma6dkfr9j5hnnn2gc0xzll4wr')
