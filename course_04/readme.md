## **1、 再复习一下taproot to tapoot 发生了什么：**

> (privatekey(1), pubkey(1)) —>  (privatekey(2), pubkey(2))
> 

## **2、做一个跟发送方相关的地址，让这个地址有丰富的含义(单节点，哈希锁定）**

<aside>
💡

**P’ = P + H(P || merkle_root) * G**

</aside>

- **P’**: Taproot 输出公钥（从地址推导）
- **P**: 内部公钥（控制块中的32字节）
- **H**: Tagged hash 函数
- **merkle_root**: 脚本树的 Merkle 根
- **G**: 椭圆曲线生成点
- **tweak**（名词）= `H(P || merkle_root)`，是一个标量值
- **tweaking**（动词）= 整个调整过程 `P → P'`
- **tweaked key** = 调整后的结果 `P'`

所以说，tweak到底发生了什么：

> (privatekey(1), pubkey(1)) —>  (privatekey(1)’, pubkey(1)’)
> 

比如有这样一个场景，Alice去创造了一个中间地址，当钱打到这个中间地址以后

<aside>
💡

```python
两种花费方式：
1. 密钥路径：Alice 可以直接用私钥花费
2. 脚本路径：任何人可以通过提供 preimage "helloworld" 来花费
```

</aside>

见代码库，文件夹： taproot_basic

01-taproot_basic_commit, 产生中间地址

02-taproot_basic_reveal_keypath， Alice签名花费(解读代码)

<aside>
💡

```python
 sig = alice_private.sign_taproot_input(
        tx,
        0,
        [medium_sending_address.to_script_pub_key()],
        [to_satoshis(input_amount)],
        script_path=False,
        tapleaf_scripts=[tr_script]  # 添加脚本树
    )
   
   思考：1、 为何要传入脚本树 2、库里隐藏的tweak过程是什么 3、alice的公钥签名，真的是alice公钥吗
```

</aside>

答案在如下

- 
    
    **1. 已知数据**
    
    alice_internal_pubkey = "0250be5fc44ec580c387bf45df275aaa8b27e2d7716af31f10eeed357d126bb4d3" internal_privkey = "私钥d" # 对应上面的公钥
    
    **2. 计算脚本的 TapLeaf Hash**
    
    tr_script = "OP_SHA256 <hash> OP_EQUALVERIFY OP_TRUE" leaf_version = "0xc0" # Tapscript 版本 leaf_data = leaf_version + encode(len(tr_script)) + tr_script tap_leaf_hash = tagged_hash("TapLeaf", leaf_data)
    
    **由于只有一个脚本，这个 hash 就是 Merkle Root**
    
    **3. 计算 tweak 值**
    
    **tweak = tagged_hash("TapTweak", internal_pubkey || merkle_root)**
    
    message = internal_pubkey + tap_leaf_hash tweak = tagged_hash("TapTweak", message)
    
    **4. 计算 tweaked 公钥 (Q = P + t*G)**
    
    tweaked_pubkey = internal_pubkey + (tweak * G)
    
    **结果就是：a46780148be98aaa861ad0b5dfc5c9b935d515c7be8c9e2bc6cedfa594e2b6d9**
    
    **5. 计算 tweaked 私钥 (d' = d + t)**
    
    tweaked_privkey = internal_privkey + tweak
    
    **6. 生成签名**
    
    **6.1 计算签名消息的 hash (sighash)**
    
    tx_data = version + inputs + outputs # 交易数据 sighash = hash_tx_for_sign(tx_data) # BIP341 定义的签名哈希算法
    
    **6.2 使用 tweaked 私钥生成 Schnorr 签名**
    
    r = generate_random_nonce() # 生成随机数 R = r * G # R 点 e = tagged_hash("BIPSchnorrDerive", R || tweaked_pubkey || sighash) s = r + e * tweaked_privkey # schnorr 签名的 s 值
    
    signature = R || s
    
    **结果就是：cd57c24a00a0685593992c4c8adbd1997d969d963c03cc0fcc152aa36936048f713e6075307923d2d7a334b7c4df4c7222fbfb558c7405daf7b723ef00887e7d**
    
    **验证过程（在节点端）：**
    
    **1. 从交易中获取 tweaked_pubkey (Q)**
    
    **2. 计算签名消息的 hash**
    
    **3. 验证 Schnorr 签名**
    
    **verify(signature, sighash, tweaked_pubkey)**
    

# **3、做一个哈希锁定+Bob签名的地址，让这个地址三种解锁方法（学习双叶子结构）**

<aside>
💡

1. 向这个 Taproot 地址发送比特币
2. 可以通过以下三种方式花费:
    - Key Path: Alice 使用她的私钥直接签名
    - Script Path 1: 任何人提供正确的 preimage 'helloworld'
    - Script Path 2: Bob 使用他的私钥签名
    

=== 脚本树结构 ===
简单的双叶子树:
ROOT
/    \
/      \
HASH     BOB
(hello  (P2PK)
world)

</aside>

见代码库，文件夹： taproot_hashlock_bob

**思考：如何照葫芦画瓢，写一个双哈希锁定的脚本**

```python
三种花费方式：
1. Script Path 1：任何人提供 preimage "helloworld" 来花费
2. Script Path 2：任何人提供 preimage "helloaaron" 来花费
3. Key Path：Alice 用私钥直接花费
```

# **3、做一个哈希锁定+哈希锁定+Bob签名的地址，让这个地址的解锁方法（学习多叶子结构）**

见代码库，文件夹： taproot_threescripts

# **4、作业**

- 构建一个 hashlock+多签+时间锁定 的三叶子脚本，并用四种方式解锁，说说你在作业过程中遇到的困难以及解决办法，以及你的发现
