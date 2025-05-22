from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2wpkhAddress, P2pkhAddress, P2trAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.script import Script
from bitcoinlib.encoding import to_bytes
import requests

import requests

def get_utxo(address, min_value):
    # 示例地址 tb1p9u76qgdsay233juzztk5xtn8kelmxswut2029c0s27stxcr6g59qupu0cw
    url = f"https://api.blockcypher.com/v1/btc/test3/addrs/{address}?unspentOnly=true"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        utxos = data.get('txrefs', [])  # BlockCypher API返回的UTXO在'txrefs'字段

        if not utxos:
            print("该地址没有未花费的交易输出（UTXO）。")
            return None

        # 遍历UTXO列表
        for utxo in utxos:
            balance = utxo['value']  # UTXO的余额字段是'value'
            print(f"UTXO余额: {balance}")
            if balance >= min_value:
                return utxo

        print(f"没有找到余额大于或等于{min_value}的UTXO。")
        return None
    else:
        print(f"请求失败，状态码：{response.status_code}")
        # 示例utxo
        utxo = {
            'tx_hash': '0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098',  
            'tx_output_n': 0,
            'value': 600
        }
        return None

# 三个输入地址到一个输出地址的转账
def three_input_address_transaction():
        private_key_wif = "cQbmoSHZ9jWnfyBoY82ZqZht9taid82beJtAYpRcwKaDSxizd37a"
        private_key = PrivateKey(private_key_wif)

        # 测试网地址
        from_legacy_address = 'msmkSKovoadUpdjbKMiancy6PnKowe4VP1'  # Legacy地址
        from_segwit_address = 'tb1qsekanny2d9fapa8538ms6ep0c0aqsjhcl3kshl'  # SegWit地址
        from_taproot_address = 'tb1pc3qlpa5yl9s8a3qtkvwe6akgqa5s4qfwdn8ch4u4pd6um9wfkukqc48z3q'  # Taproot地址
        
        to_legacy_address = 'mzCyg57PeU6KfJ1rxzcQ6BEgJaemosj8pU'

        trans_value = 500  # 每个地址转出1000聪

        # 构建交易输入
        legacy_utxo = get_utxo(from_legacy_address, trans_value)
        segwit_utxo = get_utxo(from_segwit_address, trans_value)
        taproot_utxo = get_utxo(from_taproot_address, trans_value)

        txins = []
        if legacy_utxo:
            legacy_txin = TxInput(legacy_utxo['tx_hash'], legacy_utxo['tx_output_n'])
            txins.append(legacy_txin)
        if segwit_utxo:
            segwit_txin = TxInput(segwit_utxo['tx_hash'], segwit_utxo['tx_output_n'])
            txins.append(segwit_txin)
        if taproot_utxo:
            taproot_txin = TxInput(taproot_utxo['tx_hash'], taproot_utxo['tx_output_n'])
            txins.append(taproot_txin)

        output_amount = trans_value * len(txins)

        """
        多个输入地址到一个输出地址的转账
        ！！！不理解的地方：
        1.多交易构建过程
        2.多个签名设置
        3.估计费用字段大小是分别计算每个输入，还是一起算？
        
        """

        # 构建交易输出
        txout = TxOutput(output_amount, P2pkhAddress(to_legacy_address).to_script_pub_key())

        # 构建交易
        tx = Transaction(inputs=txins, outputs=[txout], has_segwit=True)
 
        print("\n 未签名的交易：")
        print(tx.serialize())

        # Legacy地址签名
        legacy_script_code = Script(['OP_DUP', 'OP_HASH160', to_bytes(from_legacy_address), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])
        sig = private_key.sign_input(tx, 0, legacy_script_code.get_script(), trans_value)
        legacy_txin.script_sig = Script([sig, P2pkhAddress(from_legacy_address).to_script_pub_key().to_hex()])

        # SegWit地址签名
        segwit_script_code = Script(['OP_0', to_bytes(from_segwit_address)])
        sig = private_key.sign_segwit_input(tx, 1, segwit_script_code, trans_value)
        public_key = P2wpkhAddress(from_segwit_address).to_public_key().to_hex()
        tx.witnesses.append([sig, public_key])

        # Taproot地址签名
        taproot_script_code = Script(['OP_1', to_bytes(from_taproot_address)])
        sig = private_key.sign_taproot_input(tx, 2, taproot_script_code, trans_value)
        public_key = P2trAddress(from_taproot_address).to_public_key().to_hex()
        tx.witnesses.append([sig, public_key])

        # 打印签名后的交易
        print("\n 签名后的交易：")
        print(tx.serialize())()

if __name__ == "__main__":

    """
    多个输入地址到一个输出地址的转账
    ！！！不理解的地方：
    1.多交易构建过程
    2.多个签名设置
    3.估计费用字段大小是分别计算每个输入，还是一起算？
    4.签名提示索引越界是什么意思
    
    """

    # === 这个例子还不能正确运行
    three_input_address_transaction()
