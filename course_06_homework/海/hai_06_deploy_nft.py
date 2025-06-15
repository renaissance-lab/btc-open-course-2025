from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
from bitcoinutils.utils import ControlBlock
import hashlib
import json

def create_brc20_deploy_script(tick, max_supply, limit_per_mint,pubkey):
    """
    创建BRC-20代币部署脚本
    :param tick: 代币符号(4个字符)
    :param max_supply: 最大供应量
    :param limit_per_mint: 每次铸造限制
    :return: 脚本对象
    """
    # 准备BRC-20部署数据
    deploy_data = {
        "p": "brc-20",
        "op": "deploy",
        "tick": tick,
        "max": str(max_supply),
        "lim": str(limit_per_mint)
    }
    deploy_json = json.dumps(deploy_data, separators=(',', ':'))
    
    # 构建脚本
    # script = Script([
    #     'OP_FALSE',  # 触发条件：OP_IF需要栈顶为True，但BRC-20用OP_FALSE触发
    #     'OP_IF',
    #         bytes.fromhex("6f7264"),  # "ord"的hex
    #         'OP_1',  # 协议版本（BRC-20固定为1）
    #         bytes.fromhex("746578742f706c61696e3b636861727365743d7574662d38"),  # "text/plain;charset=utf-8"
    #         'OP_0',  # 数据推送方式（0表示直接嵌入）
    #         deploy_json.encode('utf-8'),  # BRC-20 JSON数据
    #     'OP_ENDIF'
    # ])

    script = Script([
        pubkey.to_x_only_hex(),
        'OP_CHECKSIG',
        'OP_FALSE',
        'OP_IF',
            b'ord'.hex(),  
            'OP_1',
            b'text/plain;charset=utf-8'.hex(),  
            'OP_0',
            deploy_json.encode('utf-8').hex(),  
        'OP_ENDIF'
    ])
    
    return script

def create_deploy_transaction():
    # 初始化测试网络
    setup('testnet')
    
    # 使用您提供的私钥
    privkey = PrivateKey('cUy4pzV9gQoog9Cfhr4JaMCpqkLaa7YAcg9xwuuEktT3PSkTDp3t')
    pubkey = privkey.get_public_key()
    own_address = pubkey.get_taproot_address()
    # tb1pwdygg20pkgg5rus0jg59tgjz3sltcqpv2pafl7g9udmuekv7rn2sryhecg
    print("taproot地址：", own_address.to_string())

    # 创建BRC-20部署脚本
    script = create_brc20_deploy_script("DIAO", 21000, 100, pubkey)

    tree = [script]
    tree_address = pubkey.get_taproot_address(tree)
    print("tree taprootd地址:", tree_address.to_string())
    
    tx_input = TxInput("036be90a2afbf736d0a2b321509627c625d42df5b2797eb74289cc2c03781be0", 0)
    
    tx_output = TxOutput(546, own_address.to_script_pub_key())
    tx_change = TxOutput(800 - 546 - 220, own_address.to_script_pub_key())

    # 创建交易
    tx = Transaction(inputs=[tx_input], outputs=[tx_output], has_segwit=True)
    
    # 签名交易
    sig = privkey.sign_taproot_input(tx, 0, [tree_address.to_script_pub_key()], [800],
                                      script_path=True, tapleaf_script=script, tweak=False)

    cb = ControlBlock(pubkey, tree, 0, is_odd=tree_address.is_odd())

    tx.witnesses.append(
        TxWitnessInput([
        sig,
        script.to_hex(),
        cb.to_hex()
        ])
    )
    
    return tx

if __name__ == "__main__":
    # 创建并打印部署交易
    deploy_tx = create_deploy_transaction()
    print("\nBRC-20部署交易:")
    print("Raw Hex:", deploy_tx.serialize())
    print("\nTxID:", deploy_tx.get_txid())