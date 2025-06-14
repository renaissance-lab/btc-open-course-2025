import os

from flask import Flask,jsonify

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from flask_cors import CORS

app = Flask (__name__)
CORS(app)

rpc_connection = AuthServiceProxy("http://dh:Server123@127.0.0.1:18332")

@app.route("/")
def hello():
    return "hello bitcoin!"

@app.route("/tx/getblockchaininfo", methods=['GET'])
# 用于获取区块链信息
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


@app.route("/tx/broadcast/<raw_tx_hex>", methods=['GET'])
def broadcast(raw_tx_hex):
    try:
        # 发送交易到网络
        rpc_connection = AuthServiceProxy("http://dh:Server123@127.0.0.1:18332")
        tx_id = rpc_connection.sendrawtransaction(raw_tx_hex)
        response = jsonify({
            "status": "success",
            "message": "交易已广播！",
            "txid": tx_id
        })
        return response
    
    except JSONRPCException as e:
        response = jsonify({
            "status": "error",
            "message": f"{e}"
        })
        return response

if __name__ == '__main__':
    prefix = os.getenv("BASE")

    print("app pid:", os.getpid())

    app.run(debug=True)