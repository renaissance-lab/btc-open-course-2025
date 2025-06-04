"""
创建一个具有三种花费方式的 Taproot 地址

三种花费方式：
1. 密钥路径：Alice 可以直接用私钥花费
2. 脚本路径：任何人(Bob)可以通过提供 preimage "helloworld" 来花费
3. 多签路径：Alice、Bob 和 Cake 可以通过三个签名中的两个进行花费

=== Taproot 地址信息 ===
Alice 将作为内部密钥使用
"""

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey, PublicKey
import hashlib
from hdwallet import HDWallet
from hdwallet.symbols import BTC, BTCTEST
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic

def create_address():
    # 设置测试网
    setup('testnet')
    
    mnemonic = "impact mouse twenty guide rate airport differ easy limb door gold axis"
    print(f"助记词: {mnemonic}")
    
    # 生成 HDWallet
    hdwallet: HDWallet = HDWallet(symbol=BTCTEST)
    hdwallet.from_mnemonic(mnemonic=mnemonic)
    
    # 1. 传统地址 (P2PKH) - BIP44
    alice_path = "m/44'/1'/0'/0/0"
    hdwallet.from_path(alice_path)
    print(f"\n传统地址 (BIP44 - {alice_path}): {hdwallet.p2pkh_address()}")
    print(f"=== 密钥信息 ({alice_path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()
    
    # 1. 创建三个参与者的密钥
    alice_private = PrivateKey(hdwallet.wif())  
    alice_public = alice_private.get_public_key()
    
    bob_path = "m/44'/1'/0'/0/1"
    hdwallet.from_path(bob_path)
    print(f"\n传统地址 (BIP44 - {bob_path}): {hdwallet.p2pkh_address()}")
    print(f"=== 密钥信息 ({bob_path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()
    
    bob_private = PrivateKey(hdwallet.wif())  # 同上
    bob_public = bob_private.get_public_key()
    
    cake_path = "m/44'/1'/0'/0/2"
    hdwallet.from_path(cake_path)
    print(f"\n传统地址 (BIP44 - {cake_path}): {hdwallet.p2pkh_address()}")
    print(f"=== 密钥信息 ({cake_path}) ===")
    print(f"私钥 (HEX): {hdwallet.private_key()}")
    print(f"私钥 (WIF): {hdwallet.wif()}")
    print(f"公钥 (压缩): {hdwallet.public_key()}")
    hdwallet.clean_derivation()
    
    cake_private = PrivateKey(hdwallet.wif())  # 同上
    cake_public = cake_private.get_public_key()
    
    # 2. 创建 preimage 的哈希（用于哈希时间锁）
    preimage = "helloworld"
    preimage_bytes = preimage.encode('utf-8')
    preimage_hash = hashlib.sha256(preimage_bytes).hexdigest()
    
    # 3. 创建脚本路径1 - 验证 preimage
    htlc_script = Script([
        'OP_SHA256',
        preimage_hash,
        'OP_EQUALVERIFY',
        'OP_TRUE'
    ])
    
    # 4. 创建脚本路径2 - 2-of-3 多签名
    multisig_script = Script([
        alice_public.to_hex(),
        'OP_CHECKSIG',
        bob_public.to_hex(),
        'OP_CHECKSIGADD',
        cake_public.to_hex(),
        'OP_CHECKSIGADD',
        'OP_2',
        'OP_EQUAL'
    ])
    
    # 5. 创建 Taproot 地址（将 Alice 的公钥作为内部密钥，并添加两个脚本路径）
    taproot_address = alice_public.get_taproot_address([[htlc_script], [multisig_script]])
    
    print("\n=== Taproot 地址信息 ===")
    print(f"Alice 私钥: {alice_private.to_wif()}")
    print(f"Alice 公钥: {alice_public.to_hex()}")
    print(f"Bob 私钥: {bob_private.to_wif()}")
    print(f"Bob 公钥: {bob_public.to_hex()}")
    print(f"Cake 私钥: {cake_private.to_wif()}")
    print(f"Cake 公钥: {cake_public.to_hex()}")
    print(f"Preimage: {preimage}")
    print(f"Preimage Hash: {preimage_hash}")
    print(f"Taproot 地址: {taproot_address.to_string()}")
    
    print("\n脚本路径信息:")
    print(f"HTLC 脚本: {htlc_script}")
    print(f"多签脚本: {multisig_script}")
    
    # 返回创建的对象供以后使用
    return {
        'alice_private': alice_private,
        'alice_public': alice_public,
        'bob_private': bob_private,
        'bob_public': bob_public,
        'cake_private': cake_private,
        'cake_public': cake_public,
        'preimage': preimage,
        'preimage_bytes': preimage_bytes,
        'preimage_hash': preimage_hash,
        'htlc_script': htlc_script,
        'multisig_script': multisig_script,
        'taproot_address': taproot_address
    }

def spend_key_path(address_info, tx_id, output_index, to_address_str, amount, change_amount=None, utxo_value=None):
    """
    花费方式1：使用 Alice 的私钥通过密钥路径花费
    """
    # 设置测试网
    setup('testnet')
    
    alice_private = address_info['alice_private']
    taproot_address = address_info['taproot_address']
    
    # 创建交易输入
    txin = TxInput(tx_id, output_index)
    
    # 创建交易输出
    to_address = taproot_address.__class__(to_address_str)
    amount_to_send = amount
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )
    
    # 准备输出列表
    outputs = [txout]
    
    # 如果有找零，添加找零输出
    if change_amount and change_amount > 0:
        change_output = TxOutput(
            to_satoshis(change_amount),
            taproot_address.to_script_pub_key()
        )
        outputs.append(change_output)
    
    # 创建交易
    tx = Transaction([txin], outputs, has_segwit=True)
    
    # 获取输入金额 (用于签名)
    input_amount = amount_to_send
    if change_amount:
        input_amount += change_amount
    
    # 估算手续费 = 从输入UTXO中扣除的部分
    fee = 0.00001  # 0.00001 BTC = 1000 satoshis 作为合理手续费
    input_amount += fee
    
    amounts = [to_satoshis(input_amount)]
    scriptPubkey = taproot_address.to_script_pub_key()
    utxos_scriptPubkeys = [scriptPubkey]
    
    # 使用 Alice 的密钥签名交易（密钥路径）
    sig = alice_private.sign_taproot_input(
        tx,
        0,  # 输入索引
        utxos_scriptPubkeys,
        [utxo_value]
    )
    
    # 添加见证数据
    tx.witnesses.append(TxWitnessInput([sig]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n密钥路径花费交易:")
    print(signed_tx)
    print("\nTxId:", tx.get_txid())
    print(f"\n主输出: {amount_to_send} BTC 到 {to_address_str}")
    if change_amount and change_amount > 0:
        print(f"找零输出: {change_amount} BTC 到 {taproot_address.to_string()}")
    print(f"交易费: {fee} BTC")
    
    return tx

def spend_script_path_htlc(address_info, tx_id, output_index, to_address_str, amount, change_amount=None):
    """
    花费方式2：使用 preimage 通过脚本路径花费
    """
    # 设置测试网
    setup('testnet')
    
    alice_public = address_info['alice_public']
    preimage_bytes = address_info['preimage_bytes']
    htlc_script = address_info['htlc_script']
    multisig_script = address_info['multisig_script']
    taproot_address = address_info['taproot_address']
    
    # 创建交易输入
    txin = TxInput(tx_id, output_index)
    
    # 创建交易输出
    to_address = taproot_address.__class__(to_address_str)
    amount_to_send = amount
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )
    
    # 准备输出列表
    outputs = [txout]
    
    # 如果有找零，添加找零输出
    if change_amount and change_amount > 0:
        change_output = TxOutput(
            to_satoshis(change_amount),
            taproot_address.to_script_pub_key()
        )
        outputs.append(change_output)
    
    # 创建交易
    tx = Transaction([txin], outputs, has_segwit=True)
    
    # 创建 control block （指定 htlc_script 是第一个脚本）
    control_block = ControlBlock(
        alice_public,
        [htlc_script, multisig_script],  # 所有脚本叶子
        0,                               # HTLC脚本的索引
        is_odd=taproot_address.is_odd()
    )
    
    # 添加见证数据 [preimage, script, control_block]
    tx.witnesses.append(TxWitnessInput([
        preimage_bytes.hex(),
        htlc_script.to_hex(),
        control_block.to_hex()
    ]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\nHTLC脚本路径花费交易:")
    print(signed_tx)
    print("\nPreimage (hex):", preimage_bytes.hex())
    print("HTLC Script (hex):", htlc_script.to_hex())
    print("Control block:", control_block.to_hex())
    print("\nTxId:", tx.get_txid())
    print(f"\n主输出: {amount} BTC 到 {to_address_str}")
    if change_amount and change_amount > 0:
        print(f"找零输出: {change_amount} BTC 到 {taproot_address.to_string()}")
    print(f"交易费: {0.00001} BTC")
    
    return tx

def spend_script_path_multisig(address_info, tx_id, output_index, to_address_str, amount, signers, change_amount=None):
    """
    花费方式3：使用2-of-3多签名通过脚本路径花费
    signers: 提供签名的两个参与者（从 'alice', 'bob', 'cake' 中选择两个）
    """
    # 设置测试网
    setup('testnet')
    
    # 获取参与者的私钥
    private_keys = []
    for signer in signers:
        if signer == 'alice':
            private_keys.append(address_info['alice_private'])
        elif signer == 'bob':
            private_keys.append(address_info['bob_private'])
        elif signer == 'cake':
            private_keys.append(address_info['cake_private'])
        else:
            raise ValueError(f"未知签名者: {signer}")
    
    if len(private_keys) != 2:
        raise ValueError("必须提供恰好两个签名者")
    
    alice_public = address_info['alice_public']
    htlc_script = address_info['htlc_script']
    multisig_script = address_info['multisig_script']
    taproot_address = address_info['taproot_address']
    
    # 创建交易输入
    txin = TxInput(tx_id, output_index)
    
    # 创建交易输出
    to_address = taproot_address.__class__(to_address_str)
    amount_to_send = amount
    txout = TxOutput(
        to_satoshis(amount_to_send),
        to_address.to_script_pub_key()
    )
    
    # 准备输出列表
    outputs = [txout]
    
    # 如果有找零，添加找零输出
    if change_amount and change_amount > 0:
        change_output = TxOutput(
            to_satoshis(change_amount),
            taproot_address.to_script_pub_key()
        )
        outputs.append(change_output)
    
    # 创建交易
    tx = Transaction([txin], outputs, has_segwit=True)
    
    # 获取输入金额 (用于签名)
    input_amount = amount_to_send
    if change_amount:
        input_amount += change_amount
    
    # 估算手续费 = 从输入UTXO中扣除的部分
    fee = 0.00001  # 0.00001 BTC = 1000 satoshis 作为合理手续费
    input_amount += fee
    
    amounts = [to_satoshis(input_amount)]
    scriptPubkey = taproot_address.to_script_pub_key()
    utxos_scriptPubkeys = [scriptPubkey]
    
    # 生成签名
    signatures = []
    for key in private_keys:
        sig = key.sign_taproot_input(
            tx,
            0,  # 输入索引
            utxos_scriptPubkeys,
            amounts,
            script_path=True
        )
        signatures.append(sig)
    
    # 创建 control block （指定 multisig_script 是第二个脚本）
    control_block = ControlBlock(
        alice_public,
        [htlc_script, multisig_script],  # 所有脚本叶子
        1,                               # 多签脚本的索引
        is_odd=taproot_address.is_odd()
    )
    
    # 添加见证数据 [空字符, sig1, sig2, script, control_block]
    tx.witnesses.append(TxWitnessInput([
        signatures[0] if signers[0] == 'alice' else '',  # 如果Alice签名，放Alice的签名，否则空
        signatures[1] if signers[0] == 'bob' or (signers[1] == 'bob' and signers[0] != 'alice') else '',  # Bob的签名位置
        signatures[0] if signers[0] == 'cake' or (signers[1] == 'cake' and signers[0] != 'alice') else signatures[1] if signers[1] == 'cake' and signers[0] == 'alice' else '',  # Cake的签名位置
        multisig_script.to_hex(),
        control_block.to_hex()
    ]))
    
    # 获取签名后的交易
    signed_tx = tx.serialize()
    
    print("\n多签脚本路径花费交易:")
    print(signed_tx)
    print(f"签名者: {signers[0]} 和 {signers[1]}")
    print("Multisig Script (hex):", multisig_script.to_hex())
    print("Control block:", control_block.to_hex())
    print("\nTxId:", tx.get_txid())
    print(f"\n主输出: {amount} BTC 到 {to_address_str}")
    if change_amount and change_amount > 0:
        print(f"找零输出: {change_amount} BTC 到 {taproot_address.to_string()}")
    print(f"交易费: {0.00001} BTC")
    
    return tx

def main():
    # 导入UTXO选择器
    from smart_utxo_selector import SmartUTXOSelector, btc_to_satoshi, satoshi_to_btc
    
    # 1. 创建地址
    print("=== 创建Taproot地址 ===")
    address_info = create_address()
    
    taproot_address = address_info['taproot_address']
    address_str = taproot_address.to_string()
    print(f"\nTaproot地址: {address_str}")
    
    # 初始化UTXO选择器
    utxo_selector = SmartUTXOSelector(network="testnet")
    
    try:
        # 获取地址的UTXO
        all_utxos = utxo_selector.get_utxos(address_str)
        
        if not all_utxos:
            print(f"\n地址 {address_str} 没有可用的UTXO，请先向该地址发送一些测试币")
            print("\n使用说明:")
            print("1. 向创建的 Taproot 地址发送一些测试币")
            print("2. 然后重新运行此脚本选择花费方式")
            print("3. 广播生成的交易到测试网:")
            print("   https://mempool.space/testnet/tx/push")
            return
        
        # 计算地址总余额
        total_balance = sum(utxo['value'] for utxo in all_utxos)
        print(f"\n地址总余额: {satoshi_to_btc(total_balance)} BTC ({total_balance} satoshis)")
        
        # 选择花费方式
        print("\n请选择花费方式:")
        print("1. 使用Alice的私钥花费（密钥路径）")
        print("2. 使用preimage花费（HTLC脚本路径）")
        print("3. 使用2-of-3多签花费（多签脚本路径）")
        
        choice = input("请选择花费方式 (1/2/3): ")
        
        if choice not in ['1', '2', '3']:
            print("无效选择")
            return
        
        # 选择花费金额
        amount_str = input(f"请输入要花费的金额 (BTC，最大 {satoshi_to_btc(total_balance)}): ")
        try:
            amount = float(amount_str)
            amount_satoshis = btc_to_satoshi(amount)
        except ValueError:
            print("无效金额")
            return
        
        if amount_satoshis > total_balance:
            print(f"错误: 花费金额 {amount} BTC 超过了可用余额 {satoshi_to_btc(total_balance)} BTC")
            return
        
        # 选择UTXO选择策略
        print("\n请选择UTXO选择策略:")
        print("1. 贪心算法 (优先选择最大的UTXO)")
        print("2. 最小找零算法 (尽量选择接近目标金额的UTXO组合)")
        print("3. 合并小额UTXO (优先选择小额UTXO，帮助清理钱包)")
        
        strategy_choice = input("请选择策略 (1/2/3，默认1): ") or "1"
        
        strategy_map = {
            "1": "greedy",
            "2": "min_change",
            "3": "consolidate"
        }
        
        if strategy_choice not in strategy_map:
            print("无效策略选择，使用默认贪心算法")
            strategy = "greedy"
        else:
            strategy = strategy_map[strategy_choice]
        
        # 估算交易费用 (假设每字节 5 sat 的费率)
        estimated_fee = utxo_selector.estimate_fee(1, 2, fee_rate=5)  # 假设1个输入，2个输出（主输出和找零）
        target_amount = amount_satoshis + estimated_fee
        
        # 选择UTXO
        try:
            selected_utxos, total_selected = utxo_selector.select_utxos(address_str, target_amount, strategy)
        except Exception as e:
            print(f"选择UTXO失败: {e}")
            return
        
        # 计算找零金额和交易费
        # 使用合理的交易费，不是全部差额
        # 先假设交易费为估算值
        actual_fee = estimated_fee
        change_amount = total_selected - amount_satoshis - actual_fee
        
        print(f"\n已选择 {len(selected_utxos)} 个UTXO，总额: {satoshi_to_btc(total_selected)} BTC")
        print(f"交易费用: {satoshi_to_btc(actual_fee)} BTC ({actual_fee} satoshis)")
        print(f"主输出金额: {satoshi_to_btc(amount_satoshis)} BTC ({amount_satoshis} satoshis)")
        print(f"找零金额: {satoshi_to_btc(change_amount)} BTC ({change_amount} satoshis)")
        
        # 使用第一个UTXO作为输入 (实际应用中可能需要多个输入)
        tx_id = selected_utxos[0]['txid']
        output_index = selected_utxos[0]['vout']
        
        # 花费到相同的地址 (Taproot地址)
        to_address = address_str
        
        # 基于选择执行相应的花费函数
        if choice == '1':
            print("\n选择密钥路径花费")
            print(f"UTXO金额: {total_selected} satoshis")
            tx = spend_key_path(address_info, tx_id, output_index, to_address, amount, change_amount=satoshi_to_btc(change_amount), utxo_value=total_selected)
            print(f"\n已创建密钥路径花费交易，TxId: {tx.get_txid()}")
        elif choice == '2':
            tx = spend_script_path_htlc(address_info, tx_id, output_index, to_address, amount, change_amount=satoshi_to_btc(change_amount))
            print(f"\n已创建HTLC脚本路径花费交易，TxId: {tx.get_txid()}")
        elif choice == '3':
            print("\n选择两个签名者:")
            print("1. Alice")
            print("2. Bob")
            print("3. Cake")
            
            signer1 = int(input("第一个签名者 (1/2/3): "))
            signer2 = int(input("第二个签名者 (1/2/3): "))
            
            if signer1 not in [1, 2, 3] or signer2 not in [1, 2, 3]:
                print("错误: 无效的签名者选择")
                return
                
            if signer1 == signer2:
                print("错误: 两个签名者必须不同")
                return
            
            signers = []
            if signer1 == 1 or signer2 == 1:
                signers.append('alice')
            if signer1 == 2 or signer2 == 2:
                signers.append('bob')
            if signer1 == 3 or signer2 == 3:
                signers.append('cake')
            
            if len(signers) != 2:
                print("错误：必须选择两个不同的签名者")
                return
            
            tx = spend_script_path_multisig(address_info, tx_id, output_index, to_address, amount, signers, change_amount=satoshi_to_btc(change_amount))
            print(f"\n已创建多签脚本路径花费交易，TxId: {tx.get_txid()}")
        
        # 显示交易广播说明
        signed_tx = tx.serialize()
        print("\n请将以下交易广播到测试网:")
        print(f"Transaction (hex): {signed_tx}")
        print("广播地址: https://mempool.space/testnet/tx/push")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


# https://mempool.space/testnet/tx/68bbdfe7281acda46043c1cc51cb57d2a9164f2183c59efe7ef236561d5aa50c