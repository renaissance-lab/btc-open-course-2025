import requests
import json

ORD_SERVER_URL = "http://127.0.0.1:80"

def get_block_height():
    response = requests.get(f"{ORD_SERVER_URL}/blockheight")
    return response.text

def get_inscription(id):
    response = requests.get(f"{ORD_SERVER_URL}/inscription/{id}")
    return response.json()

def get_inscriptions_by_block(height):
    response = requests.get(f"{ORD_SERVER_URL}/inscriptions/block/{height}")
    return response.json()

def get_sat_info(sat_number):
    response = requests.get(f"{ORD_SERVER_URL}/sat/{sat_number}")
    return response.json()

# 示例使用
if __name__ == "__main__":
    # 获取当前区块高度
    height = get_block_height()
    print(f"Current block height: {height}")
    
    # 获取特定区块的铭文
    block_inscriptions = get_inscriptions_by_block(height)
    print(f"Inscriptions in block {height}: {json.dumps(block_inscriptions, indent=2)}")
    
    # 获取特定铭文信息
    if block_inscriptions and len(block_inscriptions) > 0:
        inscription_id = block_inscriptions[0]['id']
        inscription = get_inscription(inscription_id)
        print(f"Inscription {inscription_id} details: {json.dumps(inscription, indent=2)}")