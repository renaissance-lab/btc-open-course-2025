@ChatGPT

锁定脚本（Locking Script，也叫 scriptPubKey）的结构不同。这些脚本决定了资金如何被“锁住”，以及后续如何被“解锁”（即 scriptSig 或 witness 部分）。

📌 1. Legacy（P2PKH）
	•	地址前缀：1...
	•	锁定脚本（scriptPubKey）：

OP_DUP OP_HASH160 <PubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
## ex.
addr: 1PMycacnJaSqwwJqjawXBErnLsZ7RkXUAs
scriptPubKey(ASM): OP_DUP OP_HASH160 76a04053bda0a88bda5177b86a15c3b29f559873 OP_EQUALVERIFY OP_CHECKSIG
    OP_DUP
    OP_HASH160
    OP_PUSHBYTES_20:76a04053bda0a88bda5177b86a15c3b29f559873
    OP_EQUALVERIFY
    OP_CHECKSIG
##
scriptPubKey(HEX): 76a91476a04053bda0a88bda5177b86a15c3b29f55987388ac
	•	76 → OP_DUP
	•	a9 → OP_HASH160
	•	14 → push 20 bytes
	•	76a04053bda0a88bda5177b86a15c3b29f559873 → the pubkey hash
	•	88 → OP_EQUALVERIFY
	•	ac → OP_CHECKSIG

## notes
	•	<PubKeyHash> 是 20 字节的公钥哈希。
	•	解锁脚本 (scriptSig) 提供：签名 和 原始公钥。
## 优劣
✅ 最基础、最广泛支持
❌ 不支持隔离见证（？），交易体积大、存在可塑性问题

⸻

📌 2. P2SH（兼容型 SegWit，P2SH-P2WPKH） RBF?
	•	地址前缀：3...
	•	锁定脚本（scriptPubKey）：

OP_HASH160 <RedeemScriptHash> OP_EQUAL
ex.
addr: 3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5
scriptPubKey(ASM):
    scriptPubKey: 
    OP_HASH160
    OP_PUSHBYTES_20 982a9dacf9e0365a252185cb664fca73a559bc89
    OP_EQUAL
scriptPubKey(HEX): format: a914982a9dacf9e0365a252185cb664fca73a559bc8987

## note
	•	<RedeemScriptHash> 是 redeem script 的哈希，例如：0 <20-byte-pubkey-hash>是 P2WPKH 的嵌套形式
	•	解锁时，scriptSig 会提供 redeem script；实际执行的是里面嵌套的 SegWit 结构。
## 优劣
✅ 向后兼容旧钱包
❌ 结构复杂，仍保留 scriptSig，交易体积比原生 SegWit 大

⸻

📌 3. Native SegWit（Bech32 地址）

a) P2WPKH（单签）
	•	地址前缀：bc1q...
	•	锁定脚本（scriptPubKey）：

0 <20-byte-pubkey-hash>

	•	0 是版本号（v0）
	•	后面是 20 字节的公钥哈希（与 P2PKH 相同）
	•	解锁脚本放在 witness 区域，非 scriptSig，体积更小。
## ex. V0_P2WPKH
addr: tb1q840vrzv5lfuj5m6udgc3p75m0uk888w0daves5
    OP_0
    OP_PUSHBYTES_20 3d5ec18994fa792a6f5c6a3110fa9b7f2c739dcf

b) P2WSH（多签或复杂脚本）
	•	锁定脚本（scriptPubKey）：

0 <32-byte-script-hash>

✅ 更小交易体积，支持隔离见证，降低费用
❌ 需要钱包支持 Bech32

⸻

📌 4. Taproot（P2TR）
	•	地址前缀：bc1p...
	•	锁定脚本（scriptPubKey）：

OP_1 <32-byte-x-only-pubkey>

	•	OP_1 代表 SegWit v1
	•	<x-only-pubkey> 是 32 字节的 Schnorr 公钥（不含 y 坐标）

	•	解锁方式支持两种路径：
	•	Key path：直接使用私钥签名（最简单、高效）
	•	Script path：使用 Merkle 树中的脚本（MAST），隐私更强，执行灵活条件
## ex.V1_P2TR
addr: tb1pjyjeruun8pc5ln3wtv2d6lsxqn55frpyc83kn473h7848d0kj73sxy3ku8
    OP_PUSHNUM_1
    OP_PUSHBYTES_32 912591f39338714fce2e5b14dd7e0604e9448c24c1e369d7d1bf8f53b5f697a3

✅ 更强隐私、更简洁签名、支持高级合约结构
❌ 尚未完全普及，钱包支持有限

⸻
### 总结对比表
地址类型	      ScriptPubKey 示例	                                            特点
P2PKH (Legacy)	OP_DUP OP_HASH160 <PubKeyHash> OP_EQUALVERIFY OP_CHECKSIG	签名+公钥解锁，兼容最好, 不支持witness
P2SH	        OP_HASH160 <RedeemScriptHash> OP_EQUAL	                    兼容 SegWit，嵌套结构
P2WPKH	        0 <PubKeyHash>	                                            原生 SegWit，低费率
P2WSH	        0 <ScriptHash>	                                            原生 SegWit，支持复杂脚本
P2TR (Taproot)	OP_1 <XOnlyPubKey>	                                        支持 Schnorr+MAST，隐私强
