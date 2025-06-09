
from bitcoinutils.script import Script
from bitcoinutils.keys import P2pkhAddress, PrivateKey,PublicKey,P2trAddress
import hashlib

from config import *
from btc_util import get_x_only_hex_pk_from_priv_wif, get_pk_from_priv_wif


def gen_hash_script():
    preimage = "good"
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    hash_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])
    return hash_script

def get_test_script_leaf(srcitp_priv_wif):
    privkey_tr_script = PrivateKey(srcitp_priv_wif)
    pubkey_tr_script = privkey_tr_script.get_public_key()
    tr_script_p2pk = Script([pubkey_tr_script.to_x_only_hex(), "OP_CHECKSIG"])
    return tr_script_p2pk

def buildMultiKeyScript(pks,threshold):
    if not pks or len(pks) == 0:
        raise Exception("build_multi_key_script, not pks or len(pks) == 0")
    else:
        scripts = []
        for i in range(len(pks)):
            if i==0:
                scripts.append(pks[0])
                scripts.append("OP_CHECKSIG")
            else:
                scripts.append(pks[i])
                scripts.append("OP_CHECKSIGADD")
                
        scripts.append(threshold)
        opcode = "OP_NUMEQUAL"
        scripts.append(opcode)

        return Script(scripts)

def gen_multi_sign_leaf():
    x_only_pk2 = get_x_only_hex_pk_from_priv_wif(btc_wif2)
    x_only_pk3 = get_x_only_hex_pk_from_priv_wif(btc_wif3)
    x_only_pk4 = get_x_only_hex_pk_from_priv_wif(btc_wif4)
    pks = [x_only_pk2, x_only_pk3, x_only_pk4]
    return buildMultiKeyScript(pks,2)
    # return Script([x_only_pk2, "OP_CHECKSIG"])
    # return Script(["OP_0", x_only_pk2, "OP_CHECKSIGADD", x_only_pk3, "OP_CHECKSIGADD", x_only_pk4, "OP_CHECKSIGADD", 2, "OP_EQUAL"])

TIME_LOCK = 2
def buildTimelockScript():
    x_only_pk2 = get_x_only_hex_pk_from_priv_wif(btc_wif2)
    return Script([x_only_pk2, "OP_CHECKSIGVERIFY", TIME_LOCK, "OP_CHECKSEQUENCEVERIFY"])
    # return Script([TIME_LOCK, "OP_CHECKSEQUENCEVERIFY"])

def gen_all_leafs():
    hash_script = gen_hash_script()
    multi_sign_leaf = gen_multi_sign_leaf()
    TimelockScript = buildTimelockScript()

    all_leafs = [hash_script,[multi_sign_leaf,TimelockScript]]
    return all_leafs

def get_script_path_addr():
    pub = PublicKey(btc_pubkey2)
    all_leafs = gen_all_leafs()
    print(f"all_leafs:{all_leafs}")
    taproot_address = pub.get_taproot_address(all_leafs)
    return taproot_address

    # addr = taproot_address.to_string()
    # is_odd = taproot_address.is_odd()

