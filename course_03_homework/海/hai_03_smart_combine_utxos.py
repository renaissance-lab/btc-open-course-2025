from bitcoinutils.keys import PrivateKey, P2wpkhAddress, P2trAddress
from bitcoinutils.setup import setup
from bitcoinutils.transactions import TxInput, TxOutput, Transaction, TxWitnessInput
import requests
from typing import List, Dict

'''
私钥（WIF）: cRAMZzQWNDeQRwundLs2zkyDjxKwHBFtLw63UMn8u6E8sVUhPvzQ
公钥（HEX): 03ea361d87c515d84f969d93a3a9b027369dd9237e515d8543ccd5bfa30a15df01

 === 不同类型地址 === 
Legacy地址: mkjTqSND94suFaZhyFiMfWug4Mq8mX5JSU
Segwit地址 *: tb1q8ymy0dkkpyvhxd3v7axx58k00hzuxjde4rkqdp
Taproot地址 **: tb1ptstv5wrep48f5jzpcajxj3tgksydey6m40alzry0v9q6lx63h2kq9qhtum
'''
def generate_small_utxos():
    setup('testnet')

    # 发送方的私钥
    from_private_key = PrivateKey("cVgbLBMymtebKVGoriSVWxEBahbGvvx3tuKJftGpaJBcfjujZd4C")
    from_public_key = from_private_key.get_public_key()
    # 发送方的segwit地址
    from_segwit_address = from_public_key.get_segwit_address()

    # 接收方的segwit地址
    to_segwit_address = P2wpkhAddress('tb1q8ymy0dkkpyvhxd3v7axx58k00hzuxjde4rkqdp')

    '''
    发送方地址：tb1ql67l67sy6zn6d2ztf75chu3h498ydupplwscpt
    接收方地址：tb1q8ymy0dkkpyvhxd3v7axx58k00hzuxjde4rkqdp
    '''
    print(f"\n发送方地址：{from_segwit_address.to_string()}")
    print(f"接收方地址：{to_segwit_address.to_string()}")

    # 构建交易输入
    # 交易输入的哈希值和索引
    txin = TxInput('d1d4a5382c6ab1169a29c7e5c8b24871661910a103ae98a88fd390067bdae63e',
                   2)

    # 发送方的金额
    send1 = 500
    send2 = 600
    send3 = 700
    send4 = 800
    send5 = 1600

    # 构建交易输出
    # 交易输出的金额和脚本
    txout1 = TxOutput(send1, to_segwit_address.to_script_pub_key())
    txout2 = TxOutput(send2, to_segwit_address.to_script_pub_key())
    txout3 = TxOutput(send3, to_segwit_address.to_script_pub_key())
    txout4 = TxOutput(send4, to_segwit_address.to_script_pub_key())

    # 将发送方的金额返回给自己
    txout5 = TxOutput(send5, from_segwit_address.to_script_pub_key())
    txouts = [txout1, txout2, txout3, txout4, txout5]

    # 构建交易
    tx = Transaction([txin], txouts, has_segwit=True)

    print("\n 未签名的交易：")
    print(tx.serialize())

    # 构建输入脚本
    input_script = from_public_key.get_address().to_script_pub_key()
    # 签名交易
    sig = from_private_key.sign_segwit_input(tx, 0, input_script, 5000)
    
    # 将签名添加到交易中
    tx.witnesses.append(TxWitnessInput([sig, from_public_key.to_hex()]))
    print(from_public_key.to_hex())

    signed_tx = tx.serialize()

    print("\n 已签名的交易:")
    print(signed_tx)

# 查询可用的UTXO
def request_utxo(addr,chain_name="testnet"):
    if chain_name == "testnet":
        print(f"https://mempool.space/testnet/api/address/{addr}/utxo")
        res = requests.get(f"https://mempool.space/testnet/api/address/{addr}/utxo", timeout=10).json()
    else:
        res = requests.get(f"https://mempool.space/api/address/{addr}/utxo", timeout=10).json()

    # 返回获取到的UTXO信息
    return res

def generate_utxo_combinations(target_amount: int, utxo_pool: List[Dict], strategy: str = "smallest_first") -> List[List[Dict]]:
    """
    根据目标金额生成最优UTXO组合
    
    参数:
        target_amount (int): 目标金额（以聪为单位）
        utxo_pool (List[Dict]): 可用UTXO列表，每个UTXO包含txid, vout, value等信息
    
    返回:
        List[List[Dict]]: 最优UTXO组合列表
    """
    # 按策略排序UTXO
    if strategy == "smallest_first":
        sorted_utxos = sorted(utxo_pool, key=lambda x: x["value"])
    
    # 贪心算法寻找最优组合
    selected = []
    accumulated = 0
    
    for utxo in sorted_utxos:
        if accumulated >= target_amount:
            break
        selected.append(utxo)
        accumulated += utxo["value"]
    
    if accumulated < target_amount:
        raise ValueError(f"UTXO不足，无法达到目标金额 {target_amount} 聪")
    
    # 尝试寻找更精确的组合（动态规划方法）
    def find_exact_combination(utxos, target):
        # 动态规划寻找精确组合
        dp = [None] * (target + 1)
        dp[0] = []
        
        for utxo in utxos:
            for amount in range(target, utxo["value"] - 1, -1):
                if dp[amount - utxo["value"]] is not None and dp[amount] is None:
                    dp[amount] = dp[amount - utxo["value"]] + [utxo]
        
        return dp[target]
    
    exact_combination = find_exact_combination(utxo_pool, target_amount)
    
    # 返回最优组合（优先返回精确组合）
    if exact_combination:
        return [exact_combination]
    else:
        return [selected]

# 生成txin结构
def create_txins(utxos):
    txins = []
    for utxo in utxos:
        txins.append(TxInput(utxo['txid'], utxo['vout']))

    return txins

# 生成Witness
def create_witnesses(utxos, tx, private_key=""):
    witnesses = []
    key = PrivateKey(private_key)
    pub_key = key.get_public_key()
    for i, utxo in enumerate(utxos):
        input_script = pub_key.get_address().to_script_pub_key()
        sig = key.sign_segwit_input(tx, i, input_script, utxo['value'])
        witnesses.append(TxWitnessInput([sig, pub_key.to_hex()]))
    return witnesses

def multi_utxo_transfer_by_smart_generator():
    from_address = "tb1q8ymy0dkkpyvhxd3v7axx58k00hzuxjde4rkqdp"
    to_address = "tb1ptstv5wrep48f5jzpcajxj3tgksydey6m40alzry0v9q6lx63h2kq9qhtum"
    transfer_count = 1600
    fee = 400

    utxos_request = request_utxo(from_address)
    utoxs_gen = generate_utxo_combinations(transfer_count + fee, utxos_request)

    # 打印生成的UTXO组合
    print(f"{len(utoxs_gen[0])}个utxo")
    for utxo in utoxs_gen[0]:
        print(f"\nutxo: {utxo}")

    txins = create_txins(utoxs_gen[0])

    # 将发送方的金额返回给自己
    txout = TxOutput(transfer_count, P2trAddress(to_address).to_script_pub_key())

    # 构建交易
    tx = Transaction(txins, [txout], has_segwit=True)

    print("\n 未签名的交易：")
    print(tx.serialize())

    witnesses = create_witnesses(utoxs_gen[0], tx, private_key="cRAMZzQWNDeQRwundLs2zkyDjxKwHBFtLw63UMn8u6E8sVUhPvzQ")
    tx.witnesses = []
    tx.witnesses = witnesses

    print("\n 已签名的交易:")
    print(tx.serialize())
    
if __name__ == "__main__":
    multi_utxo_transfer_by_smart_generator()