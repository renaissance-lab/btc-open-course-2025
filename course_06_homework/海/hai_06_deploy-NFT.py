from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
from bitcoinutils.utils import ControlBlock
import os

def generate_pushdata2_sequence(hex_data, max_chunk_size=520):
    """
    生成十六进制数据块的列表
    
    参数:
        hex_data (str): 图片HEX字符串（如"89504e47..."）
        max_chunk_size (int): 每块最大字节数（默认520）
    
    返回:
        list: 十六进制数据块列表
    """
    # 按520字节拆分HEX数据（每2个HEX字符=1字节）
    return [
        hex_data[i:i+max_chunk_size*2]
        for i in range(0, len(hex_data), max_chunk_size*2)
    ]

def create_nft_deploy_script(imgpath, pubkey):
    with open(imgpath, 'rb') as f:
        img = f.read()

    # 获取十六进制数据块列表
    data_chunks = generate_pushdata2_sequence(img.hex(), max_chunk_size=520)
    
    # 构建脚本 - 注意每个数据块需要单独处理
    script = Script([
        pubkey.to_x_only_hex(),
        'OP_CHECKSIG',
        'OP_FALSE',
        'OP_IF',
            b'ord'.hex(),  
            'OP_1',
            b'text/plain;charset=utf-8'.hex(),  
            'OP_0',
            *data_chunks,  # 展开所有数据块
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

    basePath = os.path.dirname(os.path.abspath(__file__))
    imgpath = os.path.join(basePath,"hai_06_leaf.JPG")
    # 创建NFT部署脚本
    script = create_nft_deploy_script(imgpath, pubkey)

    tree = [script]
    tree_address = pubkey.get_taproot_address(tree)
    print("tree taprootd地址:", tree_address.to_string())
    
    tx_input = TxInput("a8f50ffb78bb3a11ac07c7145ae5daa2889635b2a74c6a2df11dbca749e6edd3", 0)
    
    tx_output = TxOutput(546, own_address.to_script_pub_key())
    tx_change = TxOutput(800 - 546 - 0, own_address.to_script_pub_key())

    # 创建交易
    tx = Transaction(inputs=[tx_input], outputs=[tx_output], has_segwit=True)
    
    # 签名交易
    sig = privkey.sign_taproot_input(tx, 0, [tree_address.to_script_pub_key()], [5000],
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
    print("\nNFT部署交易:")
    print("Raw Hex:", deploy_tx.serialize())
    print("\ntx size: ", deploy_tx.get_size())
    print("\nTxID:", deploy_tx.get_txid())