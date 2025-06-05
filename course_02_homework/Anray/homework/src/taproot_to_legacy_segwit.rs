use bitcoin::{
    Address, Network, PrivateKey, Transaction, TxIn, TxOut, Witness,
    absolute::LockTime, transaction::Version, OutPoint, Txid, ScriptBuf,
    sighash::{SighashCache, TapSighashType}, Amount
};
use secp256k1::{Secp256k1, Message, Keypair, XOnlyPublicKey};
use std::str::FromStr;
use std::fs;
use std::collections::HashMap;
use reqwest;
use hex;

pub async fn taproot_to_legacy_segwit() -> Result<(), Box<dyn std::error::Error>> {
    // 设置测试网络
    let network = Network::Testnet;
    
    // 从配置文件读取钱包信息
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
    let keypair = Keypair::from_secret_key(&secp, &private_key.inner);
    let (xonly_public_key, _parity) = XOnlyPublicKey::from_keypair(&keypair);
    
    // 创建Taproot地址
    let from_address = Address::p2tr(&secp, xonly_public_key, None, network);
    
    // 解析目标地址
    let segwit_address = Address::from_str(&segwit_address_str)
        .unwrap()
        .require_network(network)?;
    let legacy_address = Address::from_str(&legacy_address_str)
        .unwrap()
        .require_network(network)?;
    
    println!("\n=== 验证地址 ===");
    println!("从地址 (P2TR): {}", from_address);
    println!("SegWit 地址: {}", segwit_address);
    println!("Legacy 地址: {}", legacy_address);
    
    // 创建交易输入
    let prev_txid = Txid::from_str("b99c6efe0686649b02c9e991b37d35004e91594fd19dda797ac502ed20b5021b")?;
    let prev_vout = 1;
    let outpoint = OutPoint::new(prev_txid, prev_vout);
    
    // 计算金额（单位：satoshi）
    let input_amount = Amount::from_sat(13800);
    let output_amount = Amount::from_sat(10000);
    let mut fee = Amount::from_sat(100);
    
    // 创建交易输入
    let txin = TxIn {
        previous_output: outpoint,
        script_sig: ScriptBuf::new(),
        sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
        witness: Witness::new(),
    };
    
    // 创建交易输出
    let txout1 = TxOut {
        value: output_amount,
        script_pubkey: segwit_address.script_pubkey(),
    };
    
    let change_amount = input_amount - output_amount - fee;
    let txout2 = TxOut {
        value: change_amount,
        script_pubkey: legacy_address.script_pubkey(),
    };
    
    // 创建未签名交易
    let mut tx = Transaction {
        version: Version::TWO,
        lock_time: LockTime::ZERO,
        input: vec![txin],
        output: vec![txout1.clone(), txout2.clone()],
    };
    
    println!("\n=== 未签名的交易 ===");
    println!("交易十六进制: {}", hex::encode(bitcoin::consensus::serialize(&tx)));
    println!("TxId: {}", tx.txid());
    
    // 计算Taproot签名哈希
    let mut sighash_cache = SighashCache::new(&tx);
    let sighash = sighash_cache.taproot_key_spend_signature_hash(
        0,
        &bitcoin::sighash::Prevouts::All(&[TxOut {
            value: input_amount,
            script_pubkey: from_address.script_pubkey(),
        }]),
        TapSighashType::Default,
    )?;
    
    // 签名交易
    let message = Message::from_digest_slice(&sighash[..])?;
    let signature = secp.sign_schnorr_no_aux_rand(&message, &keypair);
    
    // 添加见证数据
    let mut witness = Witness::new();
    witness.push(signature.as_ref());
    tx.input[0].witness = witness;
    
    // 获取签名后的交易
    let signed_tx_hex = hex::encode(bitcoin::consensus::serialize(&tx));
    
    println!("\n=== 已签名的交易 ===");
    println!("交易十六进制: {}", signed_tx_hex);
    
    // 重新计算手续费
    let tx_vsize = tx.vsize();
    fee = Amount::from_sat((tx_vsize as f64 * 1.05) as u64);
    println!("\n=== 重新计算手续费 ===");
    println!("交易虚拟大小: {} vbytes", tx_vsize);
    println!("重新计算手续费: {} satoshi", fee.to_sat());
    
    // 重新创建交易输出（使用新的手续费）
    let new_change_amount = input_amount - output_amount - fee;
    let new_txout2 = TxOut {
        value: new_change_amount,
        script_pubkey: legacy_address.script_pubkey(),
    };
    
    // 重新创建交易
    let mut final_tx = Transaction {
        version: Version::TWO,
        lock_time: LockTime::ZERO,
        input: vec![TxIn {
            previous_output: outpoint,
            script_sig: ScriptBuf::new(),
            sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
            witness: Witness::new(),
        }],
        output: vec![txout1, new_txout2],
    };
    
    // 重新签名
    let mut final_sighash_cache = SighashCache::new(&final_tx);
    let final_sighash = final_sighash_cache.taproot_key_spend_signature_hash(
        0,
        &bitcoin::sighash::Prevouts::All(&[TxOut {
            value: input_amount,
            script_pubkey: from_address.script_pubkey(),
        }]),
        TapSighashType::Default,
    )?;
    
    let final_message = Message::from_digest_slice(&final_sighash[..])?;
    let final_signature = secp.sign_schnorr_no_aux_rand(&final_message, &keypair);
    
    let mut final_witness = Witness::new();
    final_witness.push(final_signature.as_ref());
    final_tx.input[0].witness = final_witness;
    
    let final_signed_tx_hex = hex::encode(bitcoin::consensus::serialize(&final_tx));
    
    println!("\n=== 最终交易信息 ===");
    println!("从地址 (P2TR): {}", from_address);
    println!("到 SegWit 地址: {}", segwit_address);
    println!("找零到 Legacy 地址: {}", legacy_address);
    println!("发送金额: {} satoshi ({:.8} BTC)", output_amount.to_sat(), output_amount.to_btc());
    println!("找零金额: {} satoshi ({:.8} BTC)", new_change_amount.to_sat(), new_change_amount.to_btc());
    println!("手续费: {} satoshi ({:.8} BTC)", fee.to_sat(), fee.to_btc());
    println!("交易大小: {} bytes", final_tx.total_size());
    println!("虚拟大小: {} vbytes", final_tx.vsize());
    println!("最终交易十六进制: {}", final_signed_tx_hex);
    
    // 广播交易
    println!("\n=== 广播交易 ===");
    let mempool_api = "https://mempool.space/testnet/api/tx";
    
    let client = reqwest::Client::new();
    let response = client
        .post(mempool_api)
        .body(final_signed_tx_hex)
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