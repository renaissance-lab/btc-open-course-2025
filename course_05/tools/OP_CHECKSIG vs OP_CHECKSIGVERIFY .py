"""
对比 OP_CHECKSIG vs OP_CHECKSIGVERIFY 的区别
展示为什么2-of-2多签不能都用 OP_CHECKSIG
"""

from bitcoinutils.setup import setup
from bitcoinutils.script import Script
from bitcoinutils.keys import PrivateKey

def demonstrate_checksig_difference():
    setup('testnet')
    
    alice_private = PrivateKey('cV65Dv7Kwq8m1pG8c48UgWgx5J1Tv1TBeoTdDeVRjmQ5CpKkuPw6')
    alice_public = alice_private.get_public_key()
    
    bob_private = PrivateKey('cThG187gvrsZwnzsmPZiHW58hrhGKrfMdhAtEZKQxmwgKEdQsQ2h')
    bob_public = bob_private.get_public_key()
    
    print("=== OP_CHECKSIG vs OP_CHECKSIGVERIFY 对比 ===\n")
    
    # 脚本1：两个都用 OP_CHECKSIG（错误方式）
    wrong_script = Script([
        alice_public.to_x_only_hex(), 'OP_CHECKSIG',
        bob_public.to_x_only_hex(), 'OP_CHECKSIG'
    ])
    
    # 脚本2：正确的方式
    correct_script = Script([
        alice_public.to_x_only_hex(), 'OP_CHECKSIGVERIFY',
        bob_public.to_x_only_hex(), 'OP_CHECKSIG'
    ])
    
    print("错误脚本（两个OP_CHECKSIG）:")
    print(f"  {wrong_script}")
    print(f"  十六进制: {wrong_script.to_hex()}")
    
    print("\n正确脚本（OP_CHECKSIGVERIFY + OP_CHECKSIG）:")
    print(f"  {correct_script}")
    print(f"  十六进制: {correct_script.to_hex()}")
    
    print("\n=== 执行逻辑分析 ===")
    
    print("\n错误脚本的问题:")
    print("见证栈: [bob_sig, alice_sig]")
    print("1. alice_pubkey OP_CHECKSIG")
    print("   - 消耗 alice_sig")
    print("   - 返回 1（成功）或 0（失败）")
    print("   - 栈变成: [bob_sig, alice_result]")
    print("2. bob_pubkey OP_CHECKSIG") 
    print("   - 消耗 bob_sig")
    print("   - 返回 1（成功）或 0（失败）")
    print("   - 栈变成: [alice_result, bob_result]")
    print("3. 脚本成功条件: 栈顶非零")
    print("   - 只检查 bob_result！")
    print("   - Alice 可以提供无效签名！")
    
    print("\n正确脚本的逻辑:")
    print("见证栈: [bob_sig, alice_sig]")
    print("1. alice_pubkey OP_CHECKSIGVERIFY")
    print("   - 消耗 alice_sig")
    print("   - 验证签名，失败则脚本立即失败")
    print("   - 成功则不留栈值，栈变成: [bob_sig]")
    print("2. bob_pubkey OP_CHECKSIG")
    print("   - 消耗 bob_sig") 
    print("   - 返回 1（成功）或 0（失败）")
    print("   - 栈变成: [bob_result]")
    print("3. 脚本成功条件:")
    print("   - Alice 签名必须有效（OP_CHECKSIGVERIFY）")
    print("   - Bob 签名必须有效（OP_CHECKSIG 返回1）")
    
    print("\n=== 其他多签模式 ===")
    
    # 3个人的2-of-3（任意2个）
    print("\n真正的2-of-3多签（需要复杂脚本）:")
    print("alice_pubkey OP_CHECKSIG")
    print("bob_pubkey OP_CHECKSIG") 
    print("OP_ADD")
    print("carol_pubkey OP_CHECKSIG")
    print("OP_ADD")
    print("2 OP_GREATERTHANOREQUAL")
    print("说明：任意2个签名即可（计算签名总数 >= 2）")
    
    # 1-of-2（任意1个）
    print("\n1-of-2多签:")
    print("alice_pubkey OP_CHECKSIG")
    print("bob_pubkey OP_CHECKSIG")
    print("OP_BOOLOR")
    print("说明：Alice 或 Bob 任意一个签名即可")
    
    print("\n=== 为什么Taproot倾向于简单脚本 ===")
    print("1. 复杂脚本 → 更大的见证数据 → 更高费用")
    print("2. Key Path花费不暴露任何脚本（隐私性好）")
    print("3. Script Path适合明确的多方协作场景")
    print("4. 复杂逻辑可以用多个简单脚本组合")

if __name__ == "__main__":
    demonstrate_checksig_difference()