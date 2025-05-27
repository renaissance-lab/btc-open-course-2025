import os

from flask import Flask

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

app = Flask (__name__)

rpc_connection = AuthServiceProxy("http://dh:Server123@127.0.0.1:18332")

@app.route("/")
def hello():
    return "hello bitcoin!"

@app.route("/tx/getblockchaininfo", methods=['GET'])
def get_blockchain_info():
    try:
        blockchian_info = rpc_connection.getblockchaininfo()
        print(f"区块链信息:")
        print(f"区块高度: {blockchian_info['blocks']}")
        return blockchian_info
            
    except JSONRPCException as e:
        return f"RPC错误: {e.error}"
    except Exception as e:
        return f"其他错误: {e}"

# 测试tx 
# 02000000000101113f5c75d93510fffd0590e8d35833ee2a0bfeef28f124de12872762644505c30000000000ffffffff01ac0d000000000000160014febdfd7a04d0a7a6a84b4fa98bf237a94e46f0210140fb9ca694894ab88246436cbd37ebf321884884b46dc1f7f15253ea79f1c7bb7ded524a07d1571efa9ea94b5c1ed75db7607f6ed5edbe7e2135594e4bc0d5e61c00000000
@app.route("/tx/broadcast/<raw_tx_hex>", methods=['GET'])
def broadcast(raw_tx_hex):
    try:
        # 发送交易到网络
        tx_id = rpc_connection.sendrawtransaction(raw_tx_hex)
        return f"交易已广播！TXID: {tx_id}"
    
    except JSONRPCException as e:
        return f"广播失败: {e}"

if __name__ == '__main__':
    prefix = os.getenv("BASE")

    print("app pid:", os.getpid())

    app.run(debug=True)