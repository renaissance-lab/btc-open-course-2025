use bitcoin::{
    Address, Network, PrivateKey, PublicKey, Transaction, TxIn, TxOut, Witness,
    absolute::LockTime, transaction::Version, OutPoint, Txid, ScriptBuf,
    sighash::{SighashCache, EcdsaSighashType}, Amount
};
use secp256k1::{Secp256k1, Message};
use std::str::FromStr;
use reqwest;

pub async fn segwit_to_legacy() -> Result<(), Box<dyn std::error::Error>> {
    // 设置测试网络
    let network = Network::Testnet;
    
    // 从配置文件读取钱包信息
    use std::fs;
    use std::collections::HashMap;
    
    let config_content = fs::read_to_string("./testnet3_info.conf")?;
    let mut config_map = HashMap::new();
    
    for line in config_content.lines() {
        if let Some((key, value)) = line.split_once(" = ") {
            let clean_value = value.trim_matches('"');
            config_map.insert(key.trim(), clean_value);
        }
    }
    
    let private_key_wif = config_map.get("testnet3.private_key_wif")
        .ok_or("Missing testnet3.private_key_wif in config")?;
    let segwit_address_str = config_map.get("testnet3.segwit_address")
        .ok_or("Missing testnet3.segwit_address in config")?;
    let legacy_address_str = config_map.get("testnet3.legacy_address")
        .ok_or("Missing testnet3.legacy_address in config")?;
    
    // 创建私钥和公钥
    let private_key = PrivateKey::from_wif(&private_key_wif)?;
    let secp = Secp256k1::new();
    let public_key = PublicKey::from_private_key(&secp, &private_key);
    
    // 验证私钥
    println!("\n=== 验证私钥 ===");
    println!("Private key WIF: {}", private_key.to_wif());
    
    // 创建SegWit地址
    let from_address = Address::p2wpkh(&public_key, network).unwrap();
    println!("Generated address: {}", from_address);
    
    // 解析地址
    let segwit_address = Address::from_str(&segwit_address_str)
        .unwrap()
        .require_network(network)?;
    let legacy_address = Address::from_str(&legacy_address_str)
        .unwrap()
        .require_network(network)?;
    
    println!("\n发送方 Segwit 地址: {}", segwit_address);
    println!("接收方 legacy 地址: {}", legacy_address);
    
    // 创建交易输入
    let prev_txid = Txid::from_str("dcd1ba49acbaf58be1197c6f20513dd69d24ebb5a2a73174a2ac08c9cd3e77e3")?;
    let prev_vout = 0;
    let outpoint = OutPoint::new(prev_txid, prev_vout);
    
    // 计算金额（单位：satoshi）
    let total_input = Amount::from_btc(0.00002000)?;
    let amount_to_send = Amount::from_btc(0.00001800)?;
    let fee = Amount::from_btc(0.00000200)?;
    
    // 创建交易输入
    let tx_in = TxIn {
        previous_output: outpoint,
        script_sig: ScriptBuf::new(), // SegWit交易的script_sig为空
        sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
        witness: Witness::new(), // 稍后设置
    };
    
    // 创建交易输出
    let tx_out = TxOut {
        value: amount_to_send,
        script_pubkey: legacy_address.script_pubkey(),
    };
    
    // 创建未签名交易
    let mut tx = Transaction {
        version: Version::TWO,
        lock_time: LockTime::ZERO,
        input: vec![tx_in],
        output: vec![tx_out],
    };
    
    println!("\n未签名的交易:");
    println!("{}", hex::encode(bitcoin::consensus::serialize(&tx)));
    
    // 创建签名哈希缓存
    let mut sighash_cache = SighashCache::new(&mut tx);
    
    // 计算SegWit签名哈希
    let sighash = sighash_cache.p2wpkh_signature_hash(
        0, // 输入索引
        &segwit_address.script_pubkey(), // 脚本代码
        total_input, // 输入金额
        EcdsaSighashType::All,
    )?;
    
    // 签名
    let message = Message::from_digest_slice(&sighash[..])?;
    let signature = secp.sign_ecdsa(&message, &private_key.inner);
    
    // 创建DER编码的签名并添加sighash类型
    let mut der_sig = signature.serialize_der().to_vec();
    der_sig.push(EcdsaSighashType::All as u8);
    
    // 设置见证数据
    let witness = Witness::from_slice(&[der_sig, public_key.to_bytes()]);
    tx.input[0].witness = witness;
    
    // 获取签名后的交易
    let signed_tx_hex = hex::encode(bitcoin::consensus::serialize(&tx));
    
    println!("\n已签名的交易:");
    println!("{}", signed_tx_hex);
    
    println!("\n交易信息:");
    println!("从地址: {}", segwit_address);
    println!("到地址: {}", legacy_address);
    println!("发送金额: {} BTC", amount_to_send.to_btc());
    println!("手续费: {} BTC", fee.to_btc());
    
    // 广播交易
    println!("\n广播交易...");
    let mempool_api = "https://mempool.space/testnet/api/tx";
    
    let client = reqwest::Client::new();
    let response = client
        .post(mempool_api)
        .body(signed_tx_hex.clone())
        .send()
        .await?;
    
    if response.status().is_success() {
        let txid = response.text().await?;
        println!("交易成功！");
        println!("交易ID: {}", txid);
        println!("查看交易: https://mempool.space/testnet/tx/{}", txid);
    } else {
        let error_text = response.text().await?;
        println!("广播失败: {}", error_text);
    }
    
    Ok(())
}