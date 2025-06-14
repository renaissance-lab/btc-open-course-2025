import React, {useState} from 'react';
import './App.css';
import axios from 'axios';

function App() {
    const [searchQuery, setSearchQuery] = useState(''); // 用于顶部搜索框
    const [broadcastData, setBroadcastData] = useState(''); // 用于广播文本区域
    const [labelText, setLabelText] = useState(''); // 存储显示结果

    const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setLabelText('请输入查询内容');
      return;
    }
    // 这里添加搜索逻辑
    setLabelText(`正在查询: ${searchQuery}`);
  };

    const handleBroadcast  = async () => {
    if (!broadcastData.trim()) {
      setLabelText('请输入要广播的交易数据');
      return;
    }

      try {
        //const txData = "02000000000101113f5c75d93510fffd...";
        const url = `http://127.0.0.1:5000/tx/broadcast/${encodeURIComponent(broadcastData)}`;
        const response = await axios.get(url, {
          headers: { "Accept": "application/json" },
          responseType: 'json',
        });

        // 根据返回的status字段决定显示内容
        if (response.data.status === "success") {
          setLabelText(`交易ID: ${response.data.txid}`);
        } else if (response.data.status === "error") {
          setLabelText(`错误: ${response.data.message}`);
        } else {
          setLabelText("未知响应格式");
        }
        
      } catch (error) {
        // 处理请求失败的情况
        setLabelText(`错误: ${error.message}`);
      }
    };

    return (
    <div className="App">
        <header className="App-header">
        <img src="/logo192.png" className="App-logo" alt="logo" /> {/* 添加logo图片 */}
        <nav className="App-nav">
          <div className="App-broadcastButtonContainer">
            <button className="App-menuButton">广播</button>
          </div>
          <div className="App-searchContainer">
            <input
              type="text"
              className="App-searchInput"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="查询"
            />
            <button className="App-searchButton" onClick={handleSearch}>
              查询
            </button>
          </div>
        </nav>
        </header>
        <main className="App-main">
            <div className="App-inputContainer">
                <textarea
                    className="App-textarea"
                    value={broadcastData}
                    onChange={(e) => setBroadcastData(e.target.value)}
                    placeholder="广播内容"
                />
              <div style={{ display: 'flex', alignItems: 'center', gap: '50px' }}>
                  <button className="App-sendButton" onClick={handleBroadcast}>
                      发送
                  </button>
                  <label className="App-label">{labelText}</label>
              </div>
            </div>
        </main>
    </div>
    );
}

export default App;
