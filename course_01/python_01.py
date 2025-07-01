# ===================================
# 文件：比特币 RPC 连接示例代码
# 作者：Aaron Zhang
# 日期：2024年
# 说明：演示如何通过 RPC 连接比特币核心节点
#      并获取区块链基本信息
# ===================================

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def connect_to_bitcoin():
    # 根据你的 bitcoin.conf 配置修改这些参数
    rpc_user = ''
    rpc_password = ''  # 这个需要你提供实际使用的密码
    rpc_host = '127.0.0.1'  # localhost
    rpc_port = '8332'       # mainnet 端口
    
    rpc_connection = AuthServiceProxy(
        f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}"
    )
    try:
        # 获取区块链信息
        blockchain_info = rpc_connection.getblockchaininfo()
        print("区块链信息:")
        print(f"当前区块高度: {blockchain_info['blocks']}")
        print(f"当前区块链大小: {blockchain_info['size_on_disk']} bytes")
        print(f"是否在同步: {blockchain_info['initialblockdownload']}")
        print(f"验证进度: {blockchain_info['verificationprogress']:.2%}")
        blockchain_network = rpc_connection.getnetworkinfo()
        print(f"区块链网络: {blockchain_network}")
        blockcount = rpc_connection.getblockcount()
        print(f"当前区块高度: {blockcount}")
        blockhash = rpc_connection.getblockhash(blockcount)
        print(f"区块哈希: {blockhash}")
        block = rpc_connection.getblock(blockhash)
        print(f"区块: {block}")
        
    except JSONRPCException as e:
        print(f"RPC 错误: {e.error}")
    except Exception as e:
        print(f"连接错误: {str(e)}")

if __name__ == "__main__":
    connect_to_bitcoin()
