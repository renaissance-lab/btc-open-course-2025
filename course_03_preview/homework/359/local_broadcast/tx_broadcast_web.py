'''
比特币交易广播网页应用 (使用bitcoinutils库)

这个应用提供一个简单的Web界面，允许用户通过本地比特币测试网节点广播已签名的交易。
使用Flask框架构建Web界面，通过bitcoinutils库与比特币网络交互。
'''

from flask import Flask, render_template, request, jsonify
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction
import requests
import json
import os
import hashlib
import binascii
import io
import struct

app = Flask(__name__)

# 设置测试网
setup('testnet')

# 解析变长整数
def decode_varint(stream):
    """
    从二进制流中解析变长整数
    
    Args:
        stream (io.BytesIO): 二进制数据流
        
    Returns:
        int: 解析出的整数值
    """
    first_byte = ord(stream.read(1))
    
    if first_byte < 0xfd:
        return first_byte
    elif first_byte == 0xfd:
        return struct.unpack("<H", stream.read(2))[0]
    elif first_byte == 0xfe:
        return struct.unpack("<I", stream.read(4))[0]
    else:  # first_byte == 0xff
        return struct.unpack("<Q", stream.read(8))[0]

# 从交易十六进制字符串中提取TXID
def extract_txid_from_hex(tx_hex):
    """
    从交易的十六进制字符串中提取TXID
    
    Args:
        tx_hex (str): 交易的十六进制字符串
        
    Returns:
        str: 交易ID (TXID)
    """
    try:
        # 将十六进制字符串转换为二进制数据
        tx_binary = binascii.unhexlify(tx_hex)
        
        # 对交易数据进行双重SHA256哈希
        hash1 = hashlib.sha256(tx_binary).digest()
        hash2 = hashlib.sha256(hash1).digest()
        
        # 反转字节顺序并转换为十六进制字符串
        txid = binascii.hexlify(hash2[::-1]).decode('ascii')
        
        return txid
    except Exception as e:
        print(f"提取TXID时出错: {e}")
        return None

# 解析交易十六进制数据
def parse_transaction_hex(tx_hex):
    """
    从交易的十六进制字符串中解析交易详细信息
    
    Args:
        tx_hex (str): 交易的十六进制字符串
        
    Returns:
        dict: 包含交易详细信息的字典
    """
    try:
        # 将十六进制字符串转换为二进制数据
        tx_binary = binascii.unhexlify(tx_hex)
        stream = io.BytesIO(tx_binary)
        
        # 提取交易ID
        txid = extract_txid_from_hex(tx_hex)
        
        # 解析交易版本（4字节）
        version = struct.unpack("<I", stream.read(4))[0]
        
        # 检查是否为隔离见证交易
        marker = stream.read(1)
        is_segwit = False
        
        if marker == b'\x00':
            # 隔离见证交易有标记(0x00)和标志(0x01)
            flag = stream.read(1)
            if flag == b'\x01':
                is_segwit = True
        else:
            # 不是隔离见证交易，回退一个字节
            stream.seek(stream.tell() - 1)
        
        # 解析输入数量
        vin_count = decode_varint(stream)
        vin = []
        
        # 解析每个输入
        for i in range(vin_count):
            # 前一个交易的输出点（32字节的交易ID + 4字节的输出索引）
            prev_tx = binascii.hexlify(stream.read(32)[::-1]).decode('ascii')  # 反转字节顺序
            prev_vout = struct.unpack("<I", stream.read(4))[0]
            
            # 解析脚本长度和脚本
            script_len = decode_varint(stream)
            script = binascii.hexlify(stream.read(script_len)).decode('ascii')
            
            # 序列号
            sequence = struct.unpack("<I", stream.read(4))[0]
            
            # 添加到输入列表
            vin.append({
                'txid': prev_tx,
                'vout': prev_vout,
                'scriptSig': {'hex': script},
                'sequence': sequence
            })
        
        # 解析输出数量
        vout_count = decode_varint(stream)
        vout = []
        
        # 解析每个输出
        for i in range(vout_count):
            # 输出金额（8字节，单位为聪）
            value = struct.unpack("<Q", stream.read(8))[0]
            
            # 解析脚本长度和脚本
            script_len = decode_varint(stream)
            script = stream.read(script_len)
            script_hex = binascii.hexlify(script).decode('ascii')
            
            # 尝试识别脚本类型
            script_type = "unknown"
            address = ""
            
            # P2PKH: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
            if script[0] == 0x76 and script[1] == 0xa9 and script[2] == 0x14 and script[23] == 0x88 and script[24] == 0xac:
                script_type = "pubkeyhash"
            
            # P2SH: OP_HASH160 <scriptHash> OP_EQUAL
            elif script[0] == 0xa9 and script[1] == 0x14 and script[22] == 0x87:
                script_type = "scripthash"
            
            # P2WPKH: OP_0 <pubKeyHash>
            elif script[0] == 0x00 and script[1] == 0x14:
                script_type = "witness_v0_keyhash"
            
            # P2WSH: OP_0 <scriptHash>
            elif script[0] == 0x00 and script[1] == 0x20:
                script_type = "witness_v0_scripthash"
            
            # P2TR: OP_1 <x-only pubkey>
            elif script[0] == 0x51 and script[1] == 0x20:
                script_type = "witness_v1_taproot"
            
            # 添加到输出列表
            vout.append({
                'value': value / 100000000,  # 转换为BTC
                'n': i,
                'scriptPubKey': {
                    'hex': script_hex,
                    'type': script_type
                }
            })
        
        # 如果是隔离见证交易，解析见证数据
        witness_data = []
        if is_segwit:
            for i in range(vin_count):
                witness_count = decode_varint(stream)
                witness = []
                
                for j in range(witness_count):
                    item_len = decode_varint(stream)
                    item = binascii.hexlify(stream.read(item_len)).decode('ascii')
                    witness.append(item)
                
                witness_data.append(witness)
            
            # 将见证数据添加到对应的输入中
            for i in range(min(len(vin), len(witness_data))):
                vin[i]['txinwitness'] = witness_data[i]
        
        # 解析锁定时间（4字节）
        locktime = struct.unpack("<I", stream.read(4))[0]
        
        # 创建交易信息对象
        tx_info = {
            'txid': txid,
            'version': version,
            'locktime': locktime,
            'size': len(tx_binary),
            'vin': vin,
            'vout': vout,
            'is_segwit': is_segwit
        }
        
        return tx_info
    except Exception as e:
        print(f"解析交易时出错: {e}")
        # 如果解析失败，返回基本信息
        txid = extract_txid_from_hex(tx_hex)
        return {
            'txid': txid,
            'version': 1,  # 默认版本
            'locktime': 0,  # 默认锁定时间
            'size': len(tx_hex) // 2,  # 十六进制字符串的一半是字节数
            'vin': [],
            'vout': []
        }

# 创建templates目录
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)

# 创建HTML模板
with open(os.path.join(os.path.dirname(__file__), 'templates', 'index.html'), 'w', encoding='utf-8') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>比特币交易广播</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #f7931a;
            text-align: center;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
        }
        button {
            background-color: #f7931a;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #e78008;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .hidden {
            display: none;
        }
        .info {
            background-color: #e2f3f7;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 15px;
            cursor: pointer;
            background-color: #f1f1f1;
            border: 1px solid #ddd;
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            margin-right: 5px;
        }
        .tab.active {
            background-color: #f7931a;
            color: white;
        }
        .tab-content {
            display: none;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 0 4px 4px 4px;
            margin-bottom: 20px;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <h1>比特币交易广播</h1>
    
    <div class="container">
        <div class="tabs">
            <div class="tab active" onclick="openTab(event, 'broadcast-tab')">广播交易</div>
            <div class="tab" onclick="openTab(event, 'node-tab')">节点信息</div>
        </div>
        
        <div id="broadcast-tab" class="tab-content active">
            <div class="info">
                <p>这个工具允许你通过比特币测试网广播已签名的交易。</p>
                <p>请在下方文本框中粘贴已签名的交易十六进制数据。</p>
            </div>
            
            <form id="broadcast-form">
                <div style="margin-bottom: 15px;">
                    <label for="node-type" style="display: block; margin-bottom: 5px; font-weight: bold;">选择节点类型：</label>
                    <select id="node-type" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                        <option value="auto">自动选择 (优先本地节点)</option>
                        <option value="local">仅使用本地节点</option>
                        <option value="public">仅使用公共API</option>
                    </select>
                </div>
                <textarea id="tx-hex" placeholder="在此粘贴已签名的交易十六进制数据..."></textarea>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" style="flex: 1;">广播交易</button>
                    <button type="button" id="decode-btn" style="flex: 1; background-color: #6c757d;">解析交易</button>
                </div>
            </form>
            
            <div id="result" class="result hidden"></div>
            <div id="decode-result" class="result hidden" style="background-color: #f8f9fa; border: 1px solid #ddd; color: #212529;"></div>
        </div>
        
        <div id="node-tab" class="tab-content">
            <div class="info">
                <p>这里显示连接的比特币节点信息。</p>
            </div>
            <div id="node-info" style="background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 4px;">
                <p>正在加载节点信息...</p>
            </div>
            <button id="refresh-node-info" style="margin-top: 10px;">刷新信息</button>
        </div>
    </div>

    <script>
        // 标签页切换功能
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].className = tabcontent[i].className.replace(" active", "");
            }
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).className += " active";
            evt.currentTarget.className += " active";
            
            // 如果切换到节点信息标签，加载节点信息
            if (tabName === 'node-tab') {
                loadNodeInfo();
            }
        }
        
        // 广播交易
        document.getElementById('broadcast-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const txHex = document.getElementById('tx-hex').value.trim();
            if (!txHex) {
                showResult('请输入交易数据', false);
                return;
            }
            
            const nodeType = document.getElementById('node-type').value;
            
            fetch('/api/broadcast', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    tx_hex: txHex,
                    node_type: nodeType
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showResult(`交易广播成功！<br>交易ID: ${data.txid}<br>使用节点: ${data.node_used || '未知'}<br><a href="https://mempool.space/testnet/tx/${data.txid}" target="_blank">在区块浏览器中查看</a>`, true);
                } else {
                    showResult(`交易广播失败: ${data.error}<br>使用节点: ${data.node_used || '未知'}`, false);
                }
            })
            .catch(error => {
                showResult(`发生错误: ${error}`, false);
            });
        });
        
        // 解析交易
        document.getElementById('decode-btn').addEventListener('click', function() {
            const txHex = document.getElementById('tx-hex').value.trim();
            if (!txHex) {
                showDecodeResult('请输入交易数据');
                return;
            }
            
            const nodeType = document.getElementById('node-type').value;
            
            fetch('/api/decode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    tx_hex: txHex,
                    node_type: nodeType
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let resultHtml = `<div style="margin-bottom: 10px; font-weight: bold;">使用节点: ${data.node_used || '未知'}</div>`;
                    resultHtml += formatTransaction(data.transaction);
                    showDecodeResult(resultHtml);
                } else {
                    showDecodeResult(`解析失败: ${data.error}<br>使用节点: ${data.node_used || '未知'}`);
                }
            })
            .catch(error => {
                showDecodeResult(`发生错误: ${error}`);
            });
        });
        
        // 加载节点信息
        function loadNodeInfo() {
            fetch('/api/node_info')
            .then(response => response.json())
            .then(data => {
                const nodeInfoDiv = document.getElementById('node-info');
                if (data.success) {
                    nodeInfoDiv.innerHTML = `
                        <p><strong>网络:</strong> ${data.network}</p>
                        <p><strong>区块高度:</strong> ${data.blocks}</p>
                        <p><strong>区块头数量:</strong> ${data.headers}</p>
                        <p><strong>同步进度:</strong> ${(data.verification_progress * 100).toFixed(2)}%</p>
                        <p><strong>连接方式:</strong> ${data.connection_type}</p>
                    `;
                } else {
                    nodeInfoDiv.innerHTML = `<p>获取节点信息失败: ${data.error}</p>`;
                }
            })
            .catch(error => {
                document.getElementById('node-info').innerHTML = `<p>发生错误: ${error}</p>`;
            });
        }
        
        // 刷新节点信息
        document.getElementById('refresh-node-info').addEventListener('click', loadNodeInfo);
        
        // 显示广播结果
        function showResult(message, isSuccess) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = message;
            resultDiv.className = isSuccess ? 'result success' : 'result error';
            resultDiv.classList.remove('hidden');
            document.getElementById('decode-result').classList.add('hidden');
        }
        
        // 显示解析结果
        function showDecodeResult(message) {
            const decodeResultDiv = document.getElementById('decode-result');
            decodeResultDiv.innerHTML = message;
            decodeResultDiv.classList.remove('hidden');
            document.getElementById('result').classList.add('hidden');
        }
        
        // 格式化交易信息
        function formatTransaction(tx) {
            let html = `<h3>交易详情</h3>`;
            html += `<p><strong>交易ID:</strong> ${tx.txid}</p>`;
            html += `<p><strong>版本:</strong> ${tx.version}</p>`;
            html += `<p><strong>锁定时间:</strong> ${tx.locktime}</p>`;
            html += `<p><strong>大小:</strong> ${tx.size} 字节</p>`;
            html += `<p><strong>输入数量:</strong> ${tx.vin.length}</p>`;
            html += `<p><strong>输出数量:</strong> ${tx.vout.length}</p>`;
            
            html += `<h4>输入:</h4>`;
            tx.vin.forEach((input, index) => {
                html += `<div style="margin-bottom: 10px; padding: 5px; border-left: 3px solid #f7931a;">`;
                html += `<p><strong>输入 #${index}:</strong></p>`;
                if (input.coinbase) {
                    html += `<p>Coinbase: ${input.coinbase}</p>`;
                } else {
                    html += `<p>前一交易ID: ${input.txid}</p>`;
                    html += `<p>输出索引: ${input.vout}</p>`;
                    html += `<p>序列号: ${input.sequence}</p>`;
                }
                html += `</div>`;
            });
            
            html += `<h4>输出:</h4>`;
            tx.vout.forEach((output, index) => {
                html += `<div style="margin-bottom: 10px; padding: 5px; border-left: 3px solid #28a745;">`;
                html += `<p><strong>输出 #${index}:</strong></p>`;
                html += `<p>金额: ${output.value} BTC</p>`;
                html += `<p>地址: ${output.scriptPubKey.addresses ? output.scriptPubKey.addresses.join(', ') : '无地址'}</p>`;
                html += `<p>类型: ${output.scriptPubKey.type}</p>`;
                html += `</div>`;
            });
            
            return html;
        }
    </script>
</body>
</html>
''')

# 广播交易到比特币网络
def broadcast_transaction(tx_hex):
    """
    使用mempool.space API广播交易
    """
    try:
        # 从交易十六进制数据中提取TXID
        txid = extract_txid_from_hex(tx_hex)
        
        # 使用mempool.space API广播交易
        api_url = "https://mempool.space/testnet/api/tx"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(api_url, data=tx_hex, headers=headers)
        
        if response.status_code == 200:
            return {
                'success': True,
                'txid': txid,
                'error': None
            }
        else:
            return {
                'success': False,
                'txid': None,
                'error': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'txid': None,
            'error': str(e)
        }

# 使用本地节点广播交易
def broadcast_transaction_local(tx_hex):
    """
    使用本地比特币节点广播交易
    """
    try:
        import requests
        
        # 替换为你的比特币节点RPC凭据
        rpc_user = "username"
        rpc_password = "password"
        rpc_url = "http://127.0.0.1:18332"
        
        # 准备RPC请求
        headers = {'content-type': 'application/json'}
        payload = {
            "jsonrpc": "1.0",
            "id": "curltest",
            "method": "sendrawtransaction",
            "params": [tx_hex]
        }
        
        # 发送RPC请求
        response = requests.post(
            rpc_url,
            auth=(rpc_user, rpc_password),
            headers=headers,
            data=json.dumps(payload)
        )
        
        result = response.json()
        
        if 'result' in result:
            return {
                'success': True,
                'txid': result['result'],
                'error': None
            }
        elif 'error' in result and result['error'] is not None:
            return {
                'success': False,
                'txid': None,
                'error': f"错误代码: {result['error']['code']}, 信息: {result['error']['message']}"
            }
        else:
            return {
                'success': False,
                'txid': None,
                'error': "未知错误"
            }
    except Exception as e:
        return {
            'success': False,
            'txid': None,
            'error': str(e)
        }

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/broadcast', methods=['POST'])
def broadcast():
    try:
        data = request.get_json()
        tx_hex = data.get('tx_hex')
        node_type = data.get('node_type', 'auto')  # 默认为自动选择
        
        if not tx_hex:
            return jsonify({'success': False, 'error': '未提供交易数据'})
        
        # 根据节点类型选择广播方式
        if node_type == 'local':
            # 仅使用本地节点
            result = broadcast_transaction_local(tx_hex)
            if result['success']:
                return jsonify({
                    'success': True,
                    'txid': result['txid'],
                    'url': f'https://mempool.space/testnet/tx/{result["txid"]}',
                    'node_used': '本地节点'
                })
            else:
                return jsonify({'success': False, 'error': result['error'], 'node_used': '本地节点'})
        
        elif node_type == 'public':
            # 仅使用公共API
            result = broadcast_transaction(tx_hex)
            if result['success']:
                return jsonify({
                    'success': True,
                    'txid': result['txid'],
                    'url': f'https://mempool.space/testnet/tx/{result["txid"]}',
                    'node_used': '公共API'
                })
            else:
                return jsonify({'success': False, 'error': result['error'], 'node_used': '公共API'})
        
        else:  # auto 或其他值
            # 先尝试本地节点，失败则使用公共API
            try:
                result = broadcast_transaction_local(tx_hex)
                if result['success']:
                    return jsonify({
                        'success': True,
                        'txid': result['txid'],
                        'url': f'https://mempool.space/testnet/tx/{result["txid"]}',
                        'node_used': '本地节点'
                    })
            except Exception as e:
                print(f"本地节点广播失败，尝试使用API: {str(e)}")
            
            # 如果本地节点广播失败，使用API广播
            result = broadcast_transaction(tx_hex)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'txid': result['txid'],
                    'url': f'https://mempool.space/testnet/tx/{result["txid"]}',
                    'node_used': '公共API'
                })
            else:
                return jsonify({'success': False, 'error': result['error'], 'node_used': '公共API'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/decode', methods=['POST'])
def decode_transaction():
    try:
        data = request.get_json()
        tx_hex = data.get('tx_hex')
        node_type = data.get('node_type', 'auto')  # 默认为自动选择
        
        if not tx_hex:
            return jsonify({'success': False, 'error': '未提供交易数据'})
        
        # 根据节点类型选择解析方式
        if node_type == 'local':
            # 仅使用本地节点
            try:
                # 准备RPC请求
                rpc_user = "username"
                rpc_password = "password"
                rpc_url = "http://127.0.0.1:18332"
                
                headers = {'content-type': 'application/json'}
                payload = {
                    "jsonrpc": "1.0",
                    "id": "curltest",
                    "method": "decoderawtransaction",
                    "params": [tx_hex]
                }
                
                response = requests.post(
                    rpc_url,
                    auth=(rpc_user, rpc_password),
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                result = response.json()
                
                if 'result' in result:
                    return jsonify({
                        'success': True,
                        'transaction': result['result'],
                        'node_used': '本地节点'
                    })
                elif 'error' in result and result['error'] is not None:
                    return jsonify({
                        'success': False, 
                        'error': f"RPC错误: {result['error']['message']}",
                        'node_used': '本地节点'
                    })
            except Exception as e:
                return jsonify({
                    'success': False, 
                    'error': f"本地节点解析失败: {str(e)}",
                    'node_used': '本地节点'
                })
        
        elif node_type == 'public':
            # 仅使用自定义方法解析交易
            txid = extract_txid_from_hex(tx_hex)
            # 使用parse_transaction_hex函数解析交易（如果已实现）
            try:
                tx_info = parse_transaction_hex(tx_hex)
            except Exception:
                # 如果parse_transaction_hex未实现或失败，使用简单的交易信息对象
                tx_info = {
                    'txid': txid,
                    'version': 1,  # 默认版本
                    'locktime': 0,  # 默认锁定时间
                    'size': len(tx_hex) // 2,  # 十六进制字符串的一半是字节数
                    'vin': [],
                    'vout': []
                }
            
            return jsonify({
                'success': True,
                'transaction': tx_info,
                'node_used': '自定义解析'
            })
        
        else:  # auto 或其他值
            # 先尝试本地节点，失败则使用自定义方法
            try:
                # 准备RPC请求
                rpc_user = "username"
                rpc_password = "password"
                rpc_url = "http://127.0.0.1:18332"
                
                headers = {'content-type': 'application/json'}
                payload = {
                    "jsonrpc": "1.0",
                    "id": "curltest",
                    "method": "decoderawtransaction",
                    "params": [tx_hex]
                }
                
                response = requests.post(
                    rpc_url,
                    auth=(rpc_user, rpc_password),
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                result = response.json()
                
                if 'result' in result:
                    return jsonify({
                        'success': True,
                        'transaction': result['result'],
                        'node_used': '本地节点'
                    })
                elif 'error' in result and result['error'] is not None:
                    raise Exception(f"RPC错误: {result['error']['message']}")
            except Exception as e:
                print(f"本地节点解析失败: {str(e)}")
            
            # 如果本地节点解析失败，使用自定义方法解析交易
            txid = extract_txid_from_hex(tx_hex)
        
        # 尝试使用parse_transaction_hex函数解析交易（如果已实现）
        try:
            tx_info = parse_transaction_hex(tx_hex)
        except Exception:
            # 如果parse_transaction_hex未实现或失败，使用简单的交易信息对象
            tx_info = {
                'txid': txid,
                'version': 1,  # 默认版本
                'locktime': 0,  # 默认锁定时间
                'size': len(tx_hex) // 2,  # 十六进制字符串的一半是字节数
                'vin': [],
                'vout': []
            }
        
        return jsonify({
            'success': True,
            'transaction': tx_info,
            'node_used': '自定义解析'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/node_info')
def node_info():
    try:
        # 尝试连接本地节点获取信息
        try:
            rpc_user = "username"
            rpc_password = "password"
            rpc_url = "http://127.0.0.1:18332"
            
            headers = {'content-type': 'application/json'}
            payload = {
                "jsonrpc": "1.0",
                "id": "curltest",
                "method": "getblockchaininfo",
                "params": []
            }
            
            response = requests.post(
                rpc_url,
                auth=(rpc_user, rpc_password),
                headers=headers,
                data=json.dumps(payload)
            )
            
            result = response.json()
            
            if 'result' in result:
                info = result['result']
                return jsonify({
                    'success': True,
                    'network': info['chain'],
                    'blocks': info['blocks'],
                    'headers': info['headers'],
                    'verification_progress': info['verificationprogress'],
                    'connection_type': '本地节点'
                })
            else:
                raise Exception("无法获取节点信息")
        except Exception as e:
            print(f"本地节点连接失败: {str(e)}")
            
        # 如果本地节点连接失败，使用公共API获取信息
        response = requests.get("https://mempool.space/testnet/api/blocks/tip/height")
        blocks = int(response.text)
        
        return jsonify({
            'success': True,
            'network': 'testnet',
            'blocks': blocks,
            'headers': blocks,  # 假设同步完成
            'verification_progress': 1.0,
            'connection_type': 'mempool.space API'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 主函数
if __name__ == '__main__':
    print("启动比特币交易广播网页应用...")
    print("请在浏览器中访问: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)