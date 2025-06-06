from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2wpkhAddress, P2pkhAddress, P2trAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.script import Script

setup("testnet")

# 三个输入地址到一个输出地址的转账
def three_input_address_transaction():
        setup("testnet")

        private_key_wif = "cVgbLBMymtebKVGoriSVWxEBahbGvvx3tuKJftGpaJBcfjujZd4C"
        private_key = PrivateKey(private_key_wif)
        public_key = private_key.get_public_key()

        print(f"tap: {public_key.get_taproot_address().to_string()}")
        print(f"segwit: {public_key.get_segwit_address().to_string()}")
        print(f"legacy: {public_key.get_address().to_string()}")

        # 测试网地址
        from_taproot_address = 'tb1phsw7yj630jtay3c5vmf3mkv7kdja5889m0lmjz0h0ks8xusk03usj0xlnp'  # Taproot地址
        from_segwit_address = 'tb1ql67l67sy6zn6d2ztf75chu3h498ydupplwscpt'  # SegWit地址
        from_legacy_address = 'n4juXXS637FKJy9zJsbrCbTLvdQLRZCjST'  # Legacy地址

        to_segwit_address = 'tb1q7aum99m2j40x3gq9s056sepzjrs84py3ccnwsd'

        trans_value_tap = 4000
        trans_value_seg = 3500
        trans_value_leg = 800
        trans_total = trans_value_tap + trans_value_seg + trans_value_leg - 1000
        amount_list = [trans_value_tap, trans_value_seg, trans_value_leg]

        taproot_txin = TxInput('708bef6d8b2fe140210454d4dea5a18dc67c10ab0371b173dd7f6374323d8640', 0)
        segwit_txin = TxInput('5b35ddb78dc508852cf378f8fa5966afba4b59ae491d374def2df2ea1788341d', 0)
        legacy_txin = TxInput('c020c39014074697279a94c6f2ac67005d2e5fcbb7cee5cff275961979e5ed75', 0)
        tx_inputs = [taproot_txin, segwit_txin, legacy_txin]

        # 构建交易输出
        txout = TxOutput(trans_total, P2wpkhAddress(to_segwit_address).to_script_pub_key())

        # 构建交易
        tx = Transaction(tx_inputs, [txout], has_segwit=True)
 
        print("\n 未签名的交易：")
        print(tx.serialize())

        # 地址签名
        taproot_script = P2trAddress(from_taproot_address).to_script_pub_key()
        segwit_script = P2wpkhAddress(from_segwit_address).to_script_pub_key()
        legacy_script = P2pkhAddress(from_legacy_address).to_script_pub_key()
        script_list = [taproot_script, segwit_script, legacy_script]

        taproot_sig = private_key.sign_taproot_input(tx, 0, script_list, amount_list)
        segwit_sig = private_key.sign_segwit_input(tx, 1, segwit_script, trans_value_seg)
        legacy_sig = private_key.sign_input(tx, 2, legacy_script)

        tx_inputs[0].script_sig = Script([])
        tx_inputs[1].script_sig = Script([])
        tx_inputs[2].script_sig = Script([legacy_sig, public_key.to_hex()])

        tx.witnesses = [TxWitnessInput([taproot_sig]), TxWitnessInput([segwit_sig, public_key.to_hex()]), TxWitnessInput([])]

        # 打印签名后的交易
        print("\n 签名后的交易：")
        print(tx.serialize())

if __name__ == "__main__":
    three_input_address_transaction()