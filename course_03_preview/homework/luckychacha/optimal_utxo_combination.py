r'''
# 这个脚本目标是，按照目标金额，智能组合一个地址的多个UTXO，实现最优组合

# 1. 获取地址的UTXO
# 2. 按照金额排序
# 3. 从大到小，依次组合，直到达到目标金额
# 4. 输出组合结果


'''

import requests
from bit import PrivateKeyTestnet, PrivateKey
from datetime import datetime
import requests

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.script import Script


# 定义地址类型
class AddressType:
    P2PKH = "P2PKH"
    P2SH = "P2SH"
    P2WPKH = "P2WPKH"
    P2WSH = "P2WSH"
    P2TR = "P2TR"


# 定义账户:私钥、地址类型（枚举）
class Account:

    def __init__(self, private_key, address_type, is_testnet=True):
        self.private_key = private_key
        self.address_type = address_type
        
        if is_testnet:
            setup('testnet')
        else:
            setup('mainnet')
        

        # 私钥
        from_private_key = PrivateKey(private_key)
        from_pub = from_private_key.get_public_key()
        self.public_key = from_pub
        
        # 从同一私钥生成不同类型的地址
        if address_type == AddressType.P2PKH:
            self.address = from_pub.get_address()
        elif address_type == AddressType.P2SH:
            self.address = from_pub.get_segwit_address()
        elif address_type == AddressType.P2WPKH:
            self.address = from_pub.get_segwit_address()
        elif address_type == AddressType.P2TR:
            self.address = from_pub.get_taproot_address()

class OptimalUTXOCombination:
    # target_amount：目标金额（单位：聪）
    # private_key：私钥
    # address_type：地址类型
    # is_testnet：是否是测试网
    def __init__(self, fee, target_amount, target_address, private_key, address_type, is_testnet=True):
        # 使用 mempool.space 的测试网 API
        self.base_url = "https://mempool.space/testnet/api"
        self.target_amount = target_amount
        self.target_address = target_address
        self.account = Account(private_key, address_type, is_testnet)
        self.fee = fee

    def combine_utxos(self):
        utxos = self.get_address_utxos(self.account.address)
        if utxos is None:
            return None
        
        # 按照金额从大到小排序
        utxos.sort(key=lambda x: x['value'], reverse=True)

        utxos_to_combine = []
        # 从大到小，依次组合，直到达到目标金额
        total_amount = 0
        for utxo in utxos:
            utxos_to_combine.append(utxo)
            total_amount += to_satoshis(utxo['value'])
            if total_amount >= self.target_amount:
                return utxos_to_combine
    
    def generate_transaction(self, utxos_to_combine):
        # 创建交易对象
        tx_inputs = []
        total_input_amount = 0

        # 遍历UTXO，创建交易输入
        for utxo in utxos_to_combine:
            tx_input = TxInput(utxo['txid'], utxo['vout'])
            tx_inputs.append(tx_input)
            total_input_amount += utxo['amount']

        # 创建交易输出
        tx_output = TxOutput(self.target_amount, self.account.get_address().to_script_pub_key())
        # 找零
        change_output = TxOutput(total_input_amount - self.target_amount - self.fee, self.account.get_address().to_script_pub_key())
        if self.account.address_type == AddressType.P2PKH:
            tx = Transaction(tx_inputs, [tx_output, change_output])
        else:
            tx = Transaction(tx_inputs, [tx_output, change_output], has_segwit=True)

        # 开始签名、设置witness
        if self.account.address_type == AddressType.P2PKH:
            for i, utxo in enumerate(utxos_to_combine):
                sig = self.account.private_key.sign_input(tx, i, self.account.public_key.get_address().to_script_pub_key())
                tx_inputs[i].script_sig = Script([sig, self.account.public_key.to_hex()])

        elif self.account.address_type == AddressType.P2WPKH:
            for i, utxo in enumerate(utxos_to_combine):
                sig = self.account.private_key.sign_segwit_input(tx, i, self.account.public_key.get_address().to_script_pub_key(), to_satoshis(utxo['value']))
                tx_inputs[i].script_sig = Script([])
                tx.set_witness(i, TxWitnessInput([sig, self.account.public_key.to_hex()]))

        elif self.account.address_type == AddressType.P2TR:
            # 获取所有输入的script_pub_key, 每个都是 self.account.public_key.get_taproot_address().to_script_pub_key()
            utxo_script_pub_keys = [self.account.public_key.get_taproot_address().to_script_pub_key() for _ in range(len(utxos_to_combine))]
            amounts = [to_satoshis(utxo['value']) for utxo in utxos_to_combine]
            
            for i, utxo in enumerate(utxos_to_combine):
                tx_inputs[i].script_sig = Script([])
                sig = self.account.private_key.sign_taproot_input(tx, i, utxo_script_pub_keys, amounts)
                tx.set_witness(i, TxWitnessInput([sig]))
       

        return tx.serialize()

    def get_address_utxos(self, address):
        """获取地址的UTXO信息"""
        try:
            response = requests.get(f"{self.base_url}/address/{address}/utxo")
            if response.status_code == 200:
                utxos = []
                for utxo in response.json():
                    utxos.append({
                        'txid': utxo.get('txid'),
                        'vout': utxo.get('vout'),
                        'value': utxo.get('value', 0) / 1e8,
                        'status': utxo.get('status', {}).get('confirmed', False)
                    })
                return utxos
            return None
        except Exception as e:
            print(f"获取UTXO信息出错: {e}")
            return None


def format_btc(value):
    """将科学计数法转换为8位小数格式"""
    return f"{value:.8f}"



def main():
    fee = 400
    target_amount = 0.0001
    target_address = 'tb1p9q80mtqns48e8dm4gkuq0n5tx9zdwqqqh9skyagqrtq3q7jvdqfqe02xas'
    private_key = 'cMwQGKT54nzG2XesGda8rSPDhLuVWNr7CCbZk5UvkiBfKEdkAqwh'
    address_type = AddressType.P2TR
    is_testnet = True
    
    optimal_utxo_combination = OptimalUTXOCombination(fee, target_amount, target_address, private_key, address_type, is_testnet)
    utxos_to_combine = optimal_utxo_combination.combine_utxos()
    transaction = optimal_utxo_combination.generate_transaction(utxos_to_combine)
    print(transaction)


if __name__ == "__main__":
    main()