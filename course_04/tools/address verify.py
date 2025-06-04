"""
Taproot 地址生成器
生成不同脚本组合的地址，帮助理解为什么会有不同结果
"""

from bitcoinutils.setup import setup
from bitcoinutils.script import Script  
from bitcoinutils.keys import PrivateKey
import hashlib

def main():
    setup('testnet')
    
    # Alice 的密钥
    alice_private = PrivateKey('cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT')
    alice_public = alice_private.get_public_key()
    
    # Bob 的密钥  
    bob_private = PrivateKey('cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG')
    bob_public = bob_private.get_public_key()
    
    # 创建脚本
    preimage = "helloworld"
    preimage_hash = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
    hash_script = Script(['OP_SHA256', preimage_hash, 'OP_EQUALVERIFY', 'OP_TRUE'])
    bob_script = Script([bob_public.to_hex(), 'OP_CHECKSIG'])
    
    print("=== 不同脚本组合生成的地址对比 ===\n")
    
    # 1. 只有 Alice 公钥 (纯 Key Path)
    addr1 = alice_public.get_taproot_address()
    print(f"1. 纯 Key Path (只有 Alice):")
    print(f"   地址: {addr1.to_string()}")
    print(f"   用途: 只能用 Alice 私钥花费")
    
    # 2. Alice + 单个哈希脚本 (你能工作的)
    addr2 = alice_public.get_taproot_address([[hash_script]])
    print(f"\n2. Alice + 哈希脚本 (你能工作的):")
    print(f"   地址: {addr2.to_string()}")
    print(f"   用途: Alice Key Path 或 哈希 Script Path")
    
    # 3. Alice + 两个脚本 (简单列表)
    addr3 = alice_public.get_taproot_address([hash_script, bob_script])
    print(f"\n3. Alice + 两个脚本 (简单列表):")
    print(f"   地址: {addr3.to_string()}")
    print(f"   用途: Alice Key Path 或 两种 Script Path")
    
    # 4. Alice + 两个脚本 (嵌套结构)
    try:
        addr4 = alice_public.get_taproot_address([[hash_script, bob_script]])
        print(f"\n4. Alice + 两个脚本 (嵌套结构):")
        print(f"   地址: {addr4.to_string()}")
        print(f"   用途: Alice Key Path 或 两种 Script Path")
    except Exception as e:
        print(f"\n4. 嵌套结构失败: {e}")
    
    # 5. 三脚本复杂结构 (你原来尝试的)
    carol_private = PrivateKey('cThG187gvrsZwnzsmPZiHW58hrhGKrfMdhAtEZKQxmwgKEdQsQ2h')
    carol_public = carol_private.get_public_key()
    
    # 一个简单的 Carol 脚本
    carol_script = Script([carol_public.to_hex(), 'OP_CHECKSIG'])
    
    try:
        addr5 = alice_public.get_taproot_address([[hash_script, bob_script], [carol_script]])
        print(f"\n5. 复杂三脚本结构:")
        print(f"   地址: {addr5.to_string()}")
        print(f"   用途: Alice Key Path 或 三种 Script Path")
    except Exception as e:
        print(f"\n5. 复杂结构失败: {e}")
    
    print(f"\n=== 总结 ===")
    print(f"✅ 地址 2 能工作: {addr2.to_string()}")
    print(f"🔄 测试地址 3: {addr3.to_string()}")
    print(f"📝 每个不同的脚本组合都会生成不同的地址！")
    print(f"📝 需要向对应地址发送资金才能测试花费。")
    
    print(f"\n=== 建议测试顺序 ===")
    print(f"1. 向地址 3 发送少量测试资金")
    print(f"2. 测试 Alice Key Path 花费") 
    print(f"3. 测试哈希 Script Path 花费")
    print(f"4. 测试 Bob Script Path 花费")

if __name__ == "__main__":
    main()