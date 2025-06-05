# 比特币交易广播网页应用

这是一个简单的Web应用程序，允许用户通过本地比特币测试网节点或mempool.space API广播已签名的比特币交易。该应用使用Flask框架构建Web界面，通过bitcoinutils库与比特币网络交互。

## 功能特点

- 提供简洁的Web界面用于广播已签名的比特币交易
- 支持通过本地比特币测试网节点广播交易
- 当本地节点不可用时，自动回退到使用mempool.space API
- 支持解析交易数据，显示详细的交易信息
- 显示节点连接状态和区块链信息
- 提供交易成功后的区块浏览器链接

## 安装要求

- Python 3.6+
- Flask
- bitcoinutils
- requests

## 安装步骤

1. 确保已安装Python 3.6或更高版本

2. 安装所需的Python库：

```bash
pip install flask bitcoinutils requests
```

3. 如果要使用本地比特币节点功能，请确保您有一个运行中的比特币测试网节点，并在`bitcoin.conf`文件中配置了RPC访问：

```
testnet=1
server=1
rpcuser=username
rpcpassword=password
rpcallowip=127.0.0.1
```

4. 修改应用中的RPC连接信息：

打开`tx_broadcast_web_bitcoinutils.py`文件，找到以下代码部分并修改为你的节点RPC凭据：

```python
# 替换为你的比特币节点RPC凭据
rpc_user = "username"  # 修改为您的RPC用户名
rpc_password = "password"  # 修改为您的RPC密码
rpc_url = "http://127.0.0.1:18332"  # 如果端口不同，请修改
```

## 使用方法

1. 运行应用程序：

```bash
python tx_broadcast_web_bitcoinutils.py
```

2. 在浏览器中访问：http://127.0.0.1:5000

3. 在Web界面中，您可以：
   - 粘贴已签名的交易十六进制数据并广播
   - 解析交易数据查看详细信息
   - 查看节点连接状态和区块链信息

## 与mempool.space的区别

这个应用程序提供了类似于mempool.space/testnet/tx/push的功能，但有以下区别：

1. **本地节点优先**：优先尝试通过本地节点广播交易，只有在本地节点不可用时才使用mempool.space API
2. **交易解析功能**：提供内置的交易解析功能，无需跳转到其他网站
3. **节点信息**：显示连接的节点信息和区块链状态
4. **自托管**：可以在自己的服务器上运行，不依赖第三方服务

## 注意事项

- 此应用程序默认连接到比特币测试网，不要用于主网交易
- 在生产环境中使用前，请确保添加适当的安全措施（如HTTPS、身份验证等）
- 请确保您的RPC凭据安全，不要将其暴露在公共代码中
- 交易一旦广播到网络就无法撤回，请谨慎操作

## 开发者信息

这个应用程序是作为比特币开发课程的一部分创建的，旨在演示如何使用bitcoinutils库与比特币网络交互，并提供一个简单的Web界面进行交易广播。