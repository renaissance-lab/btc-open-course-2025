import requests
import json

ORD_SERVER_URL = "http://127.0.0.1:80"

def get_block_height():
    response = requests.get(f"{ORD_SERVER_URL}/blockheight")
    return response.text

# 示例使用
if __name__ == "__main__":
    # 获取当前区块高度
    height = get_block_height()
    print(f"Current block height: {height}")