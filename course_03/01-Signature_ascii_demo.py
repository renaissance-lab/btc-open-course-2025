#!/usr/bin/env python3
"""
签名过程可视化演示
用ASCII艺术和动画效果展示签名的每一步
"""

import time
import hashlib
import secrets

def print_slowly(text: str, delay: float = 0.03):
    """逐字打印文本，创建动画效果"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def draw_signature_step_by_step():
    """逐步绘制签名过程"""
    print("🎬 签名过程动画演示")
    print("=" * 50)
    
    print("\n🎯 场景：Alice要给Bob转账")
    time.sleep(1)
    
    # 第1步：准备消息
    print("\n📝 第1步：准备消息")
    message = "转账100 BTC给Bob"
    print(f"消息内容：'{message}'")
    
    # 画一个消息框
    print("┌" + "─" * 30 + "┐")
    print(f"│ {message:^28} │")
    print("└" + "─" * 30 + "┘")
    time.sleep(1)
    
    # 第2步：哈希消息
    print("\n🔄 第2步：对消息进行哈希")
    msg_hash = hashlib.sha256(message.encode()).hexdigest()[:8]
    print(f"消息 → 哈希函数 → {msg_hash}")
    
    print("┌─────────┐    ┌─────────┐    ┌─────────┐")
    print("│  消息   │───▶│ SHA256  │───▶│ 哈希值  │")
    print("│ (原文)  │    │ (搅拌)  │    │ (摘要)  │")
    print("└─────────┘    └─────────┘    └─────────┘")
    time.sleep(1)
    
    # 第3步：使用私钥签名
    print("\n🔐 第3步：Alice使用私钥签名")
    alice_private = secrets.randbelow(10000)
    alice_public = alice_private * 7 % 10000
    
    print(f"Alice的私钥（秘密）：{alice_private}")
    print(f"Alice的公钥（公开）：{alice_public}")
    
    # 简化的签名过程
    random_k = secrets.randbelow(10000)
    sig_r = (random_k * 7) % 10000
    sig_s = (random_k + alice_private * int(msg_hash, 16)) % 10000
    
    print("\n签名计算过程：")
    print("┌─────────┐    ┌─────────┐    ┌─────────┐")
    print("│ 哈希值  │    │ Alice   │    │  签名   │")
    print(f"│ {msg_hash} │ ＋ │ 私钥{alice_private:4d} │ ＝ │({sig_r:4d},{sig_s:4d})│")
    print("│ (消息)  │    │ (身份)  │    │ (证明)  │")
    print("└─────────┘    └─────────┘    └─────────┘")
    time.sleep(1)
    
    # 第4步：验证签名
    print("\n✅ 第4步：任何人都可以验证签名")
    print("验证需要：消息 + Alice公钥 + 签名")
    
    print("验证过程：")
    print("┌─────────┐    ┌─────────┐    ┌─────────┐")
    print("│  消息   │    │ Alice   │    │  签名   │")
    print(f"│ {message[:8]}..│ ＋ │ 公钥{alice_public:4d} │ ＋ │({sig_r:4d},{sig_s:4d})│")
    print("└─────────┘    └─────────┘    └─────────┘")
    print("              ↓")
    print("        ┌─────────────┐")
    print("        │  验证结果    │")
    print("        │    ✓ 有效    │")
    print("        └─────────────┘")
    
    return alice_private, alice_public, (sig_r, sig_s), msg_hash

def demonstrate_aggregation_visual():
    """可视化演示公钥聚合"""
    print("\n\n🧪 Schnorr聚合魔法演示")
    print("=" * 50)
    
    print("场景：Alice、Bob、Charlie要共同签署一个交易")
    
    # 三个人的密钥
    people = [
        ("Alice", secrets.randbelow(1000), "👩"),
        ("Bob", secrets.randbelow(1000), "👨"),
        ("Charlie", secrets.randbelow(1000), "🧑")
    ]
    
    print("\n👥 参与者：")
    for name, private, emoji in people:
        public = private * 7 % 1000
        print(f"{emoji} {name}: 私钥={private:3d}, 公钥={public:3d}")
    
    time.sleep(1)
    
    # 显示传统方法
    print("\n🔧 传统方法 (ECDSA)：")
    print("每个人独立签名：")
    
    print("┌─────────┐  ┌─────────┐  ┌─────────┐")
    print("│ Alice   │  │  Bob    │  │ Charlie │")
    print("│ 签名A   │  │ 签名B   │  │ 签名C   │")
    print("└─────────┘  └─────────┘  └─────────┘")
    print("     ↓            ↓            ↓")
    print("┌─────────────────────────────────────┐")
    print("│        三个独立的签名                │")
    print("│    A + B + C (物理混合)              │")
    print("└─────────────────────────────────────┘")
    
    time.sleep(2)
    
    # 显示Schnorr方法
    print("\n⚡ Schnorr方法：")
    print("步骤1：公钥聚合")
    
    print("┌─────────┐  ┌─────────┐  ┌─────────┐")
    for name, private, emoji in people:
        public = private * 7 % 1000
        print(f"│ {emoji} {public:3d}   │", end="  ")
    print()
    print("└─────────┘  └─────────┘  └─────────┘")
    
    # 计算聚合公钥
    aggregated_pubkey = sum(private * 7 for _, private, _ in people) % 1000
    
    print("     ↓            ↓            ↓")
    print("          🧪 数学魔法 🧪")
    print("              ↓")
    print("        ┌─────────────┐")
    print(f"        │ 聚合公钥    │")
    print(f"        │    {aggregated_pubkey:3d}       │")
    print("        └─────────────┘")
    
    time.sleep(2)
    
    print("\n步骤2：协作签名")
    print("🤝 第一轮 - 每人生成承诺：")
    
    nonces = []
    commitments = []
    
    for name, private, emoji in people:
        nonce = secrets.randbelow(1000)
        commitment = nonce * 7 % 1000
        nonces.append(nonce)
        commitments.append(commitment)
        print(f"{emoji} {name}: 随机数={nonce:3d}, 承诺={commitment:3d}")
    
    R = sum(commitments) % 1000
    print(f"🔗 聚合承诺: {R:3d}")
    
    time.sleep(1)
    
    print("\n✍️ 第二轮 - 生成最终签名：")
    message = "共同转账1000 BTC"
    challenge = int(hashlib.sha256(f"{R}{aggregated_pubkey}{message}".encode()).hexdigest(), 16) % 1000
    
    signature_parts = []
    for i, (name, private, emoji) in enumerate(people):
        s_part = (nonces[i] + challenge * private) % 1000
        signature_parts.append(s_part)
        print(f"{emoji} {name}: 签名部分={s_part:3d}")
    
    final_s = sum(signature_parts) % 1000
    
    print("\n🧪 化学反应过程：")
    print("┌─────┐  ┌─────┐  ┌─────┐")
    print("│ s1  │ +│ s2  │ +│ s3  │ = 融合")
    print(f"│{signature_parts[0]:3d} │  │{signature_parts[1]:3d} │  │{signature_parts[2]:3d} │")
    print("└─────┘  └─────┘  └─────┘")
    print("            ↓")
    print("     ┌─────────────┐")
    print("     │  最终签名    │")
    print(f"     │ ({R:3d}, {final_s:3d}) │")
    print("     └─────────────┘")
    
    time.sleep(1)
    
    print(f"\n📊 神奇的对比：")
    print("┌────────────────┬──────────────────┐")
    print("│   ECDSA传统    │   Schnorr聚合    │")
    print("├────────────────┼──────────────────┤")
    print("│ 3个独立签名    │ 1个聚合签名      │")
    print("│ 每个都可见     │ 融合不可分       │")
    print("│ 明显多人参与   │ 看似单人签名     │")
    print("│ 数据量大       │ 数据量小         │")
    print("└────────────────┴──────────────────┘")

def show_privacy_magic():
    """展示隐私魔法"""
    print("\n\n🎭 隐私魔法演示")
    print("=" * 50)
    
    print("让我们看看外人眼中的区别：")
    time.sleep(1)
    
    print("\n👀 区块链观察者看到的：")
    
    # 模拟单签交易
    single_sig = secrets.randbelow(10000)
    print(f"交易A: 签名 = {single_sig:4d}")
    print("       看起来像：👤 (单个人)")
    
    # 模拟Schnorr聚合签名
    aggregated_sig = secrets.randbelow(10000)
    print(f"交易B: 签名 = {aggregated_sig:4d}")
    print("       看起来像：👤 (单个人)")
    
    time.sleep(1)
    
    print("\n🤔 观察者的困惑：")
    print("┌─────────────────────────────────────┐")
    print("│ 这两个交易看起来完全一样！          │")
    print("│ 无法分辨哪个是单签，哪个是多签      │")
    print("│ 这就是Schnorr的隐私魔法            │")
    print("└─────────────────────────────────────┘")
    
    print("\n🎯 实际情况：")
    print("交易A: 真的是1个人签名 👤")
    print("交易B: 实际是3个人聚合签名 👥👥👥")
    print("       但外表看起来完全相同！")

def explain_why_aggregation_works():
    """解释为什么聚合能工作"""
    print("\n\n🔬 深层原理：为什么聚合签名能工作？")
    print("=" * 50)
    
    print("让我用简单数学来解释：")
    time.sleep(1)
    
    print("\n📐 数学基础（简化版）：")
    print("假设我们有3个人：")
    
    # 简单的数学示例
    a, b, c = 5, 7, 3  # 私钥
    print(f"Alice私钥: a = {a}")
    print(f"Bob私钥:   b = {b}")
    print(f"Charlie私钥: c = {c}")
    
    print(f"\n对应的公钥（私钥 × 基点G）：")
    print(f"Alice公钥: A = {a} × G")
    print(f"Bob公钥:   B = {b} × G")  
    print(f"Charlie公钥: C = {c} × G")
    
    print(f"\n🔗 聚合公钥：")
    print(f"聚合公钥 = A + B + C")
    print(f"         = {a}×G + {b}×G + {c}×G")
    print(f"         = ({a}+{b}+{c}) × G")
    print(f"         = {a+b+c} × G")
    
    print(f"\n✍️ 聚合签名：")
    print(f"每个人计算: si = ri + challenge × 私钥i")
    print(f"Alice: s1 = r1 + e×{a}")
    print(f"Bob:   s2 = r2 + e×{b}")
    print(f"Charlie: s3 = r3 + e×{c}")
    
    print(f"\n🧮 聚合过程：")
    print(f"s_total = s1 + s2 + s3")
    print(f"        = (r1 + e×{a}) + (r2 + e×{b}) + (r3 + e×{c})")
    print(f"        = (r1+r2+r3) + e×({a}+{b}+{c})")
    print(f"        = R_total + e × 聚合私钥")
    
    print(f"\n✅ 验证原理：")
    print(f"验证者检查: s_total × G = R_total + e × 聚合公钥")
    print(f"这个等式成立，说明签名有效！")
    
    time.sleep(2)
    
    print(f"\n💡 关键洞察：")
    print("1. 椭圆曲线的线性性质使聚合成为可能")
    print("2. (a+b+c)×G = a×G + b×G + c×G")
    print("3. 聚合后的签名在数学上等价于单个签名")
    print("4. 这就是为什么外人无法区分单签和多签")

def demonstrate_real_world_analogy():
    """现实世界类比"""
    print("\n\n🌍 现实世界类比")
    print("=" * 50)
    
    print("让我用几个生活例子来解释：")
    time.sleep(1)
    
    print("\n🎨 例子1：调色盘")
    print("ECDSA (物理混合):")
    print("  🔴 红色颜料 + 🔵 蓝色颜料 + 🟡 黄色颜料")
    print("  = 🎨 混合颜料（仍能分离出原色）")
    
    print("\nSchnorr (化学反应):")
    print("  🔴 红元素 + 🔵 蓝元素 + 🟡 黄元素")
    print("  = 🟣 新化合物（无法逆转分离）")
    
    time.sleep(2)
    
    print("\n🍲 例子2：做菜")
    print("ECDSA:")
    print("  🥕 胡萝卜 + 🥔 土豆 + 🥩 牛肉")
    print("  = 🍲 炖菜（仍能挑出每种食材）")
    
    print("\nSchnorr:")
    print("  🌾 面粉 + 🥚 鸡蛋 + 🥛 牛奶")
    print("  = 🍰 蛋糕（无法分离出原料）")
    
    time.sleep(2)
    
    print("\n🎵 例子3：音乐")
    print("ECDSA:")
    print("  🎸 吉他声 + 🥁 鼓声 + 🎤 人声")
    print("  = 🎵 混音（可以调节各轨音量）")
    
    print("\nSchnorr:")
    print("  🎼 三个音符")
    print("  = 🎶 和弦（产生全新的和声效果）")

def interactive_quiz():
    """互动测验"""
    print("\n\n🎯 理解测验")
    print("=" * 50)
    
    questions = [
        {
            "question": "如果有5个人用Schnorr聚合签名，外人能看出有几个人参与吗？",
            "options": ["A. 能看出5个人", "B. 看起来像1个人", "C. 看起来像2-3个人"],
            "answer": "B",
            "explanation": "这就是Schnorr的魔法！无论多少人参与，聚合签名看起来都像单个人的签名。"
        },
        {
            "question": "ECDSA多重签名最像什么？",
            "options": ["A. 化学反应", "B. 物理混合", "C. 核聚变"],
            "answer": "B", 
            "explanation": "ECDSA就像物理混合，每个组分（签名）都保持独立，可以分别识别。"
        },
        {
            "question": "Schnorr聚合的最大优势是什么？",
            "options": ["A. 更快的速度", "B. 隐私保护", "C. 更简单的代码"],
            "answer": "B",
            "explanation": "最大优势是隐私保护：无法区分单签和多签，提供了完美的隐私性。"
        }
    ]
    
    score = 0
    for i, q in enumerate(questions):
        print(f"\n问题 {i+1}: {q['question']}")
        for option in q['options']:
            print(f"  {option}")
        
        print(f"\n💡 答案: {q['answer']}")
        print(f"解释: {q['explanation']}")
        time.sleep(2)

if __name__ == "__main__":
    print("🎬 签名技术可视化教学")
    print("让复杂概念变得简单易懂")
    
    # 逐步演示基础签名
    alice_private, alice_public, signature, msg_hash = draw_signature_step_by_step()
    
    # 演示聚合过程
    demonstrate_aggregation_visual()
    
    # 展示隐私特性
    show_privacy_magic()
    
    # 解释深层原理
    explain_why_aggregation_works()
    
    # 现实世界类比
    demonstrate_real_world_analogy()
    
    # 互动测验
    interactive_quiz()
    
    print(f"\n🎓 课程总结")
    print("=" * 50)
    print("🔑 核心概念：")
    print("1. 数字签名 = 私钥对消息的数学指纹")
    print("2. ECDSA = 物理混合，每个签名独立存在")
    print("3. Schnorr = 化学反应，多个签名融合为一")
    print("4. 公钥聚合 = 多个身份合并成一个联合身份")
    print("5. 隐私魔法 = 外人无法区分单签和多签")
    print("6. 这些特性是Taproot革命性改进的基础！")
    
    print(f"\n🚀 下一步：")
    print("现在您已经理解了Schnorr聚合签名的核心原理，")
    print("接下来可以学习Taproot如何利用这些特性")
    print("实现更强大的比特币智能合约功能！")