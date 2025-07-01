"""
使用 bitcoinlib 创建 SegWit 到 SegWit 的测试网交易

注意事项：
1. SegWit 交易必须指定 witness_type='segwit'，而不是使用 script_type='p2wpkh'
   - Input 对象需要设置 witness_type
   - Transaction 对象也需要设置 witness_type
   
2. SegWit 交易的输入必须包含 value 参数（即 UTXO 的金额）
   - 这是 SegWit 的一个安全特性
   - 传统交易不需要这个参数，但 SegWit 必须
   - 如果不提供会导致签名验证失败
   
3. bitcoinlib 的优势：
   - 支持多种交易类型（Legacy, SegWit, Native SegWit）
   - 只需要修改少量参数就能切换不同类型
   - 内置了完整的交易验证
   - 自动处理序列化和反序列化
   
4. 可能遇到的问题：
   - 参数名称可能与其他库不同（比如 witness_type vs script_type）
   - 某些参数的文档不够清晰（比如 SegWit 必须的 value 参数）
   - 错误信息可能不够直观

使用示例：
>>> create_and_send_segwit_transaction(
>>>     private_key='cPeon9fB...',
>>>     prev_txid='6334d4...',
>>>     prev_output_n=0,
>>>     to_address='tb1qzc...',
>>>     amount=800,
>>>     input_value=1000,  # 必须指定！
>>>     broadcast=True
>>> )


关键要点：
1. 必须在 Transaction 构造函数中指定 witness_type='segwit'
2. 手续费通常比 Legacy 交易低（因为 witness discount）

常见错误及解决方案：
- "TX decode failed"：检查交易格式是否正确
- "bad-txns-inputs-missingorspent"：检查 UTXO 是否存在且未被花费
- "min relay fee not met"：增加手续费
- 广播失败：确保在正确的网络广播

"""

from bitcoinlib.transactions import Transaction, Input, Output
from bitcoinlib.keys import Key
from bitcoinlib.keys import Address
from tools.tools_broadcast import broadcast_transaction, print_broadcast_result

def create_and_send_segwit_transaction(
    private_key: str,
    prev_txid: str,
    prev_output_n: int,
    to_address: str,
    amount: int,
    input_value: int,
    broadcast: bool = False
):
    """
    创建并发送 SegWit 交易
    
    参数:
        private_key: WIF 格式的私钥
        prev_txid: 前一个交易的 ID
        prev_output_n: 前一个交易的输出索引
        to_address: 接收地址
        amount: 发送金额（单位：satoshis）
        input_value: 输入的金额（单位：satoshis）
        broadcast: 是否广播交易
    """
    
    # 创建密钥对象
    ki = Key(private_key, network='testnet')

    # 获取公钥
    # public_key = ki.public_hex  # 获取十六进制格式的公钥
    # 或者
    public_key = ki.public_byte  # 获取字节格式的公钥

    # 创建 SegWit 地址
    segwit_address = Address(data=public_key, 
                            network='testnet',
                            witness_type='segwit',  # 或 'p2sh-segwit'
                            encoding='bech32')      # bech32 编码
    print(f"\nSegWit 地址: {segwit_address.address}")


    # 创建输入 - SegWit 格式
    transaction_input = Input(
        prev_txid=prev_txid,
        output_n=prev_output_n,
        keys=ki.public(),
        network='testnet',
        witness_type='segwit',
        value=input_value
    )
    
    # 创建输出
    transaction_output = Output(
        value=amount,
        address=to_address,
        network='testnet'
    )
    
    # 创建交易
    t = Transaction(
        [transaction_input], 
        [transaction_output], 
        network='testnet',
        witness_type='segwit'
    )
    
    # 签名
    t.sign(ki.private_byte)
    
    # 输出结果
    print(f"\nRaw transaction: {t.raw_hex()}")
    print(f"Verified: {t.verify()}")
    
    
    return t.raw_hex()

def main():
    # 测试参数
    private_key = 'cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG'
    prev_txid = '42835b0a60ba12fe72f9bd5eff0b7531177ee156db8865a00f88fa499cf84a39'
    prev_output_n = 0
    to_address = 'tb1p9u76qgdsay233juzztk5xtn8kelmxswut2029c0s27stxcr6g59qupu0cw'
    amount = 600  # satoshis
    input_value = 800  # 输入的金额，单位 satoshis
    
    # 创建并广播交易
    create_and_send_segwit_transaction(
        private_key=private_key,
        prev_txid=prev_txid,
        prev_output_n=prev_output_n,
        to_address=to_address,
        amount=amount,
        input_value=input_value,
        broadcast=True
    )

if __name__ == "__main__":
    main() 