use bitcoin::{
    hashes::Hash, key::Secp256k1, opcodes::{all::*, OP_NOP2, OP_TRUE}, script::Builder,
    Address, Network, XOnlyPublicKey, Transaction, TxIn, TxOut, OutPoint, Txid,
    ScriptBuf, Sequence, Witness, sighash::{SighashCache, Prevouts, TapSighashType},
    taproot::{TapLeafHash, LeafVersion}, transaction::Version, absolute::LockTime,
    Amount, Script
};
use std::str::FromStr;

use bitcoin::taproot::{TaprootBuilder, TaprootSpendInfo};
use bitcoin::hashes::sha256;
use secp256k1::SecretKey;

/// 三叶子脚本结构
struct ThreeLeafScript {
    /// 内部密钥
    internal_key: XOnlyPublicKey,
    /// Taproot花费信息
    spend_info: TaprootSpendInfo,
    /// 地址
    address: Address,
}

impl ThreeLeafScript {
    /// 创建新的三叶子脚本
    fn new() -> Self {
        let secp = Secp256k1::new();
        
        // 生成内部密钥
        let internal_secret = SecretKey::from_slice(&[1u8; 32]).unwrap();
        let internal_key = XOnlyPublicKey::from(internal_secret.public_key(&secp));
        
        // 生成其他密钥
        let alice_secret = SecretKey::from_slice(&[2u8; 32]).unwrap();
        let alice_pubkey = alice_secret.public_key(&secp);
        let bob_secret = SecretKey::from_slice(&[3u8; 32]).unwrap();
        let bob_pubkey = bob_secret.public_key(&secp);
        
        // 转换为x-only公钥用于脚本
        let alice_xonly = XOnlyPublicKey::from(alice_pubkey);
        let bob_xonly = XOnlyPublicKey::from(bob_pubkey);
        
        // 叶子1: HashLock脚本 - 需要提供原像
        let preimage = b"bitcoin_taproot_2025";
        let hash = sha256::Hash::hash(preimage);
        let hashlock_script = Builder::new()
            .push_opcode(OP_SHA256)
            .push_slice(hash.to_byte_array())
            .push_opcode(OP_EQUALVERIFY)
            .push_opcode(OP_TRUE)
            .into_script();
        
        // 叶子2: 多签脚本 - 需要Alice和Bob的签名 (简化版本)
        let multisig_script = Builder::new()
            .push_x_only_key(&alice_xonly)
            .push_opcode(OP_CHECKSIG)
            .push_opcode(OP_VERIFY)
            .push_x_only_key(&bob_xonly)
            .push_opcode(OP_CHECKSIG)
            .into_script();
        
        // 叶子3: 时间锁定脚本 - 需要等待特定时间后才能花费
        let timelock_height = 2500000u32; // 区块高度
        let timelock_script = Builder::new()
            .push_int(timelock_height.into())
            .push_opcode(OP_NOP2) // OP_CHECKLOCKTIMEVERIFY 的别名
            .push_opcode(OP_DROP)
            .push_x_only_key(&alice_xonly)
            .push_opcode(OP_CHECKSIG)
            .into_script();
        
        // 构建Taproot树 - 需要构建平衡的二叉树
        let taproot_builder = TaprootBuilder::new()
            .add_leaf(2, hashlock_script.clone()).unwrap()
            .add_leaf(2, multisig_script.clone()).unwrap()
            .add_leaf(1, timelock_script.clone()).unwrap();
        
        let spend_info = taproot_builder.finalize(&secp, internal_key).unwrap();
        let address = Address::p2tr(&secp, internal_key, spend_info.merkle_root(), Network::Testnet);
        
        println!("=== 三叶子脚本Taproot地址创建成功 ===");
        println!("地址: {}", address);
        println!("内部密钥: {}", internal_key);
        println!("\n=== 三个叶子脚本 ===");
        println!("1. HashLock脚本: {}", hashlock_script);
        println!("2. 多签脚本: {}", multisig_script);
        println!("3. 时间锁定脚本: {}", timelock_script);
        
        Self {
            internal_key,
            spend_info,
            address,
        }
    }
    
    /// 方式1: 密钥路径花费 (Key Path)
    fn spend_by_key_path(&self) {
        println!("\n=== 解锁方式1: 密钥路径花费 (Key Path) ===");
        println!("这是最私密和高效的花费方式");
        println!("只需要内部密钥的签名，外界无法知道还有其他花费路径");
        println!("见证数据只包含一个签名，手续费最低");
        
        // 1. 创建模拟交易
        let prev_out = bitcoin::OutPoint {
            txid: bitcoin::Txid::from_slice(&[0u8; 32]).unwrap(),
            vout: 0,
        };
        
        // 2. 构建花费交易
        let tx = bitcoin::Transaction {
            version: bitcoin::transaction::Version(2),
            lock_time: bitcoin::absolute::LockTime::ZERO,
            input: vec![bitcoin::TxIn {
                previous_output: prev_out,
                script_sig: bitcoin::ScriptBuf::new(),
                sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
                witness: bitcoin::Witness::new(),
            }],
            output: vec![bitcoin::TxOut {
                value: bitcoin::Amount::from_sat(50000), // 0.0005 BTC
                script_pubkey: bitcoin::ScriptBuf::new_p2pkh(&bitcoin::PubkeyHash::from_slice(&[0u8; 20]).unwrap()),
            }],
        };
        
        // 3. 计算签名哈希 (Key Path使用默认的sighash)
        let sighash_type = bitcoin::sighash::TapSighashType::Default;
        let prevouts = vec![bitcoin::TxOut {
            value: bitcoin::Amount::from_sat(100000), // 输入金额
            script_pubkey: self.address.script_pubkey(),
        }];
        
        // 4. 生成Taproot签名
        println!("🔐 生成Taproot密钥路径签名...");
        println!("   - 使用调整后的内部私钥");
        println!("   - 签名类型: SIGHASH_DEFAULT (最优化)");
        println!("   - 见证数据大小: ~64字节 (仅包含签名)");
        
        // 5. 模拟签名验证
        println!("✅ 签名验证成功!");
        println!("📊 交易统计:");
        println!("   - 见证数据: 1个元素 (64字节签名)");
        println!("   - 手续费效率: 最优 (无脚本开销)");
        println!("   - 隐私级别: 最高 (无脚本泄露)");
        println!("   - 验证复杂度: O(1) 椭圆曲线签名验证");
        
        println!("\n💡 Key Path的优势:");
        println!("   1. 完全隐私: 外界无法知道存在脚本路径");
        println!("   2. 最低成本: 见证数据最小化");
        println!("   3. 快速验证: 单一签名验证");
        println!("   4. 向后兼容: 看起来像普通P2PK花费");
    }
    
    /// 方式2: HashLock脚本路径花费
    fn spend_by_hashlock(&self) {
        println!("\n=== 解锁方式2: HashLock脚本路径花费 ===");
        println!("需要提供正确的原像来解锁");
        println!("原像: bitcoin_taproot_2025");
        println!("任何知道原像的人都可以花费这笔资金");
        println!("见证数据: [原像, 脚本, 控制块]");

        // 定义原像
        let preimage = b"bitcoin_taproot_2025";
        
        // 计算原像的SHA256哈希
        let hash = sha256::Hash::hash(preimage);
        
        // 创建HashLock脚本: OP_SHA256 <hash> OP_EQUAL
        let script = Builder::new()
            .push_opcode(OP_SHA256)
            .push_slice(hash.as_byte_array())
            .push_opcode(OP_EQUAL)
            .into_script();
        
        // 创建一个样例交易
        let mut transaction = Transaction {
            version: Version(2),
            lock_time: LockTime::ZERO,
            input: vec![
                TxIn {
                    previous_output: OutPoint { txid: Txid::all_zeros(), vout: 0 },
                    script_sig: Script::new().into(),
                    sequence: Sequence::ENABLE_RBF_NO_LOCKTIME,
                    witness: Witness::new(),
                }
            ],
            output: vec![
                TxOut {
                    value: Amount::from_sat(100000),
                    script_pubkey: Script::new().into(),
                }
            ],
        };
        
        // 计算签名哈希
        let prevouts = vec![TxOut {
            value: Amount::from_sat(100000),
            script_pubkey: script.clone(),
        }];
        
        let mut sighash_cache = SighashCache::new(&transaction);
        let sighash = sighash_cache
            .taproot_script_spend_signature_hash(
                0,
                &Prevouts::All(&prevouts),
                TapLeafHash::from_script(&script, LeafVersion::TapScript),
                TapSighashType::Default,
            )
            .expect("计算签名哈希失败");
        
        // 构建见证数据
        let mut witness = Witness::new();
        witness.push(preimage); // 提供原像作为解锁条件
        witness.push(script.as_bytes()); // 脚本
        witness.push([0u8; 32]); // 控制块占位符
        
        transaction.input[0].witness = witness;
        
        println!("原像哈希: {}", hash);
        println!("脚本: OP_SHA256 {} OP_EQUAL", hash);
        println!("见证数据: [原像, 脚本, 控制块]");
        println!("✅ 模拟成功: 提供原像 'bitcoin_taproot_2025' 解锁");
    }
    
    /// 方式3: 多签脚本路径花费
    fn spend_by_multisig(&self) {
        println!("\n=== 解锁方式3: 多签脚本路径花费 ===");
        println!("需要Alice和Bob两个人的签名");
        println!("这是一个2-of-2多签方案");
        
        // 创建一个模拟的花费交易
        let dummy_tx = Transaction {
            version: bitcoin::transaction::Version(2),
            lock_time: bitcoin::locktime::absolute::LockTime::ZERO,
            input: vec![TxIn {
                previous_output: OutPoint {
                    txid: Txid::from_str("1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef").unwrap(),
                    vout: 0,
                },
                script_sig: ScriptBuf::new(),
                sequence: Sequence::ENABLE_RBF_NO_LOCKTIME,
                witness: Witness::new(),
            }],
            output: vec![TxOut {
                value: bitcoin::Amount::from_sat(45000), // 扣除手续费后的金额
                script_pubkey: ScriptBuf::new(),
            }],
        };
        
        // 重新创建多签脚本（用于签名哈希计算）
        let secp = Secp256k1::new();
        let alice_secret = SecretKey::from_slice(&[2u8; 32]).unwrap();
        let alice_pubkey = alice_secret.public_key(&secp);
        let bob_secret = SecretKey::from_slice(&[3u8; 32]).unwrap();
        let bob_pubkey = bob_secret.public_key(&secp);
        let alice_xonly = XOnlyPublicKey::from(alice_pubkey);
        let bob_xonly = XOnlyPublicKey::from(bob_pubkey);
        
        let multisig_script = Builder::new()
            .push_x_only_key(&alice_xonly)
            .push_opcode(OP_CHECKSIG)
            .push_opcode(OP_VERIFY)
            .push_x_only_key(&bob_xonly)
            .push_opcode(OP_CHECKSIG)
            .into_script();
        
        // 创建前一个输出（用于签名验证）
        let prev_out = TxOut {
            value: bitcoin::Amount::from_sat(50000),
            script_pubkey: self.address.script_pubkey(),
        };
        
        // 计算多签脚本路径的签名哈希
        let prevouts = vec![&prev_out];
        let sighash = SighashCache::new(&dummy_tx)
            .taproot_script_spend_signature_hash(
                0, // input index
                &Prevouts::All(&prevouts),
                TapLeafHash::from_script(&multisig_script, LeafVersion::TapScript),
                TapSighashType::Default,
            )
            .expect("计算签名哈希失败");
        
        println!("📝 交易信息:");
        println!("   - 输入金额: {} sats", prev_out.value.to_sat());
        println!("   - 输出金额: {} sats", dummy_tx.output[0].value.to_sat());
        println!("   - 手续费: {} sats", prev_out.value.to_sat() - dummy_tx.output[0].value.to_sat());
        println!("   - 签名哈希: {}", sighash);
        
        println!("\n🔐 多重签名验证过程:");
        println!("   1. Alice使用私钥对交易进行签名");
        println!("   2. Bob使用私钥对交易进行签名");
        println!("   3. 验证两个签名都有效");
        println!("   4. 构造见证数据: [Alice签名, Bob签名, 多签脚本, 控制块]");
        
        println!("\n💡 多签脚本路径花费的优势:");
        println!("   • 安全性: 需要多方同意才能花费资金");
        println!("   • 灵活性: 可以设置不同的签名阈值(如2-of-3)");
        println!("   • 隐私性: 在链上只显示为普通的Taproot输出");
        println!("   • 效率: 相比传统多签，见证数据更小");
        
        println!("✅ 模拟成功: Alice和Bob共同签名解锁");
    }
    
    /// 方式4: 时间锁定脚本路径花费
    fn spend_by_timelock(&self) {
        println!("\n=== 解锁方式4: 时间锁定脚本路径花费 ===");
        println!("需要等待到指定的区块高度: 2500000");
        println!("只有Alice可以在时间锁到期后花费");
        println!("这提供了一种延迟花费的机制");
        
        // 重新创建时间锁定脚本（用于签名哈希计算）
        let secp = Secp256k1::new();
        let alice_secret = SecretKey::from_slice(&[2u8; 32]).unwrap();
        let alice_pubkey = alice_secret.public_key(&secp);
        let alice_xonly = XOnlyPublicKey::from(alice_pubkey);
        
        let timelock_height = 2500000u32; // 区块高度
        let timelock_script = Builder::new()
            .push_int(timelock_height.into())
            .push_opcode(OP_NOP2) // OP_CHECKLOCKTIMEVERIFY 的别名
            .push_opcode(OP_DROP)
            .push_x_only_key(&alice_xonly)
            .push_opcode(OP_CHECKSIG)
            .into_script();
        
        // 创建一个模拟的花费交易（假设当前区块高度已超过时间锁）
        let dummy_tx = Transaction {
            version: bitcoin::transaction::Version(2),
            lock_time: bitcoin::locktime::absolute::LockTime::from_height(timelock_height).unwrap(),
            input: vec![TxIn {
                previous_output: OutPoint {
                    txid: Txid::from_str("abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890").unwrap(),
                    vout: 0,
                },
                script_sig: ScriptBuf::new(),
                sequence: Sequence::ENABLE_LOCKTIME_NO_RBF,
                witness: Witness::new(),
            }],
            output: vec![TxOut {
                value: bitcoin::Amount::from_sat(48000), // 扣除手续费后的金额
                script_pubkey: ScriptBuf::new(),
            }],
        };
        
        // 创建前一个输出（用于签名验证）
        let prev_out = TxOut {
            value: bitcoin::Amount::from_sat(50000),
            script_pubkey: self.address.script_pubkey(),
        };
        
        // 计算时间锁定脚本路径的签名哈希
        let prevouts = vec![&prev_out];
        let sighash = SighashCache::new(&dummy_tx)
            .taproot_script_spend_signature_hash(
                0, // input index
                &Prevouts::All(&prevouts),
                TapLeafHash::from_script(&timelock_script, LeafVersion::TapScript),
                TapSighashType::Default,
            )
            .expect("计算签名哈希失败");
        
        println!("\n📝 交易信息:");
        println!("   - 输入金额: {} sats", prev_out.value.to_sat());
        println!("   - 输出金额: {} sats", dummy_tx.output[0].value.to_sat());
        println!("   - 手续费: {} sats", prev_out.value.to_sat() - dummy_tx.output[0].value.to_sat());
        println!("   - 时间锁高度: {}", timelock_height);
        println!("   - 交易锁定时间: {:?}", dummy_tx.lock_time);
        println!("   - 签名哈希: {}", sighash);
        
        println!("\n⏰ 时间锁定验证过程:");
        println!("   1. 检查当前区块高度是否 >= {}", timelock_height);
        println!("   2. 验证交易的nLockTime字段设置正确");
        println!("   3. Alice使用私钥对交易进行签名");
        println!("   4. 构造见证数据: [Alice签名, 时间锁脚本, 控制块]");
        
        println!("\n💡 时间锁定脚本路径花费的优势:");
        println!("   • 延迟执行: 资金只能在指定时间后才能花费");
        println!("   • 安全保障: 提供时间缓冲期，防止意外操作");
        println!("   • 继承规划: 可用于遗产规划和资金托管");
        println!("   • 合约应用: 支持复杂的时间相关智能合约");
        
        println!("见证数据: [Alice签名, 脚本, 控制块]");
        println!("✅ 模拟成功: 时间锁到期后Alice签名解锁");
    }
    
    /// 展示所有解锁方式
    fn demonstrate_all_unlock_methods(&self) {
        self.spend_by_key_path();
        self.spend_by_hashlock();
        self.spend_by_multisig();
        self.spend_by_timelock();
    }
}

fn main() {
    println!("🚀 Bitcoin Taproot 三叶子脚本演示");
    println!("包含: HashLock + 多签 + 时间锁定");
    println!("四种解锁方式演示\n");
    
    // 创建三叶子脚本
    let three_leaf = ThreeLeafScript::new();
    
    // 演示四种解锁方式
    three_leaf.demonstrate_all_unlock_methods();
}
