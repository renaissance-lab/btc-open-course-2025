use bitcoin::{
    Address, Network, PrivateKey, PublicKey, Transaction, TxIn, TxOut, Witness,
    absolute::LockTime, transaction::Version, OutPoint, Txid, ScriptBuf,
    sighash::{SighashCache, TapSighashType, EcdsaSighashType}, Amount,
    script::PushBytesBuf
};
use secp256k1::{Secp256k1, Message, Keypair, XOnlyPublicKey};
use std::str::FromStr;
use std::fs;
use std::collections::HashMap;
use reqwest;
use hex;

pub async fn legacy_segwit_taproot_to_legacy() -> Result<(), Box<dyn std::error::Error>> {
    // 设置测试网络
    let network = Network::Testnet;

    println!("=== 三种输入类型到Legacy地址转账 ===");
    
    // 读取配置文件
    let config_content = fs::read_to_string("./testnet3_info.conf")?;
    let mut config = HashMap::new();
    
    for line in config_content.lines() {
        if let Some((key, value)) = line.split_once(" = ") {
            let clean_value = value.trim_matches('"');
            config.insert(key.trim(), clean_value);
        }
    }
    
    // 使用默认的私钥（如果配置文件中没有）
    let private_key_wif = config.get("testnet3.private_key_wif")
        .map_or("cMahea7zqjxrtgAbB7LSGbcQUr1uX1ojuat9jZodMN87JcbXMTcA", |v| v); // 示例私钥
    let legacy_address = config.get("testnet3.legacy_address")
        .ok_or("Missing legacy_address in config")?;
    let segwit_address = config.get("testnet3.segwit_address")
        .ok_or("Missing segwit_address in config")?;
    
    // 创建私钥和地址
    let private_key = PrivateKey::from_wif(private_key_wif)?;
    let secp = Secp256k1::new();
    let public_key = PublicKey::from_private_key(&secp, &private_key);
    let keypair = Keypair::from_secret_key(&secp, &private_key.inner);
    let (xonly_public_key, _parity) = XOnlyPublicKey::from_keypair(&keypair);
    
    // 生成Taproot地址
    let taproot_address = Address::p2tr(&secp, xonly_public_key, None, network);
    
    // 解析地址
    let legacy_addr = Address::from_str(legacy_address)?.require_network(network)?;
    let segwit_addr = Address::from_str(segwit_address)?.require_network(network)?;
    let taproot_addr = taproot_address;
    
    println!("Legacy地址: {}", legacy_addr);
    println!("SegWit地址: {}", segwit_addr);
    println!("Taproot地址: {}", taproot_addr);
    
    // UTXO信息
    let txid1 = "d9f85db96ee9f3bcb728444af4ce3b5b682ac2051cdc44d2f0173023f3453347";
    let vout1 = 0;
    let txid2 = "b99c6efe0686649b02c9e991b37d35004e91594fd19dda797ac502ed20b5021b";
    let vout2 = 0;
    let txid3 = "cb88f7bdc9ec4ab7ce7594fb905bbd413e96ff95c166ecfa05fd2c12c45b54a6";
    let vout3 = 1;
    
    let amount1 = Amount::from_sat(1800);
    let amount2 = Amount::from_sat(3000);
    let amount3 = Amount::from_sat(2400);
    let amounts = vec![amount1, amount2, amount3];
    let fee = Amount::from_sat(350);
    
    // 创建scriptPubKey
    let script_pubkey1 = legacy_addr.script_pubkey();
    let script_pubkey2 = segwit_addr.script_pubkey();
    let script_pubkey3 = taproot_addr.script_pubkey();
    let utxos_script_pubkeys = vec![script_pubkey1.clone(), script_pubkey2.clone(), script_pubkey3.clone()];
    
    // SegWit的scriptPubKey（P2WPKH）
    let segwit_script_pubkey = Address::p2wpkh(&public_key, network).expect("Failed to create P2WPKH address").script_pubkey();
    
    println!("\nsegwit_pub_key: {}", script_pubkey2.to_hex_string());
    println!("script_pub_key: {}", segwit_script_pubkey.to_hex_string());
    
    // 目标地址（Legacy）
    let to_address = legacy_addr.clone();
    
    // 创建交易输入
    let txin1 = TxIn {
        previous_output: OutPoint {
            txid: Txid::from_str(txid1)?,
            vout: vout1,
        },
        script_sig: ScriptBuf::new(),
        sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
        witness: Witness::new(),
    };
    
    let txin2 = TxIn {
        previous_output: OutPoint {
            txid: Txid::from_str(txid2)?,
            vout: vout2,
        },
        script_sig: ScriptBuf::new(),
        sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
        witness: Witness::new(),
    };
    
    let txin3 = TxIn {
        previous_output: OutPoint {
            txid: Txid::from_str(txid3)?,
            vout: vout3,
        },
        script_sig: ScriptBuf::new(),
        sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
        witness: Witness::new(),
    };
    
    // 计算总输出金额
    let total_input = amount1 + amount2 + amount3;
    let output_amount = total_input - fee;
    
    // 创建交易输出
    let txout = TxOut {
        value: output_amount,
        script_pubkey: to_address.script_pubkey(),
    };
    
    // 创建交易
    let mut tx = Transaction {
        version: Version::TWO,
        lock_time: LockTime::ZERO,
        input: vec![txin1, txin2, txin3],
        output: vec![txout],
    };
    
    println!("\n原始交易: {}", hex::encode(bitcoin::consensus::serialize(&tx)));
    println!("\ntxid: {}", tx.txid());
    println!("wtxid: {}", tx.wtxid());
    
    // 签名第一个输入（Legacy P2PKH）
    let sighash1 = SighashCache::new(&tx).legacy_signature_hash(
        0,
        &script_pubkey1,
        EcdsaSighashType::All.to_u32(),
    )?;
    let message1 = Message::from_digest_slice(&sighash1[..])?;
    let signature1 = secp.sign_ecdsa(&message1, &private_key.inner);
    let mut sig1_bytes = signature1.serialize_der().to_vec();
    sig1_bytes.push(EcdsaSighashType::All.to_u32() as u8);
    
    // 为Legacy输入设置scriptSig
    let sig1_push = PushBytesBuf::try_from(sig1_bytes.clone()).unwrap();
    let pubkey1_push = PushBytesBuf::try_from(public_key.to_bytes()).unwrap();
    tx.input[0].script_sig = ScriptBuf::builder()
        .push_slice(&sig1_push)
        .push_slice(&pubkey1_push)
        .into_script();
    
    // 签名第二个输入（SegWit P2WPKH）
    let sighash2 = SighashCache::new(&tx).p2wpkh_signature_hash(
        1,
        &segwit_script_pubkey,
        amount2,
        EcdsaSighashType::All,
    )?;
    let message2 = Message::from_digest_slice(&sighash2[..])?;
    let signature2 = secp.sign_ecdsa(&message2, &private_key.inner);
    let mut sig2_bytes = signature2.serialize_der().to_vec();
    sig2_bytes.push(EcdsaSighashType::All.to_u32() as u8);
    
    // 为SegWit输入设置witness
    tx.input[1].witness.push(&sig2_bytes);
    tx.input[1].witness.push(&public_key.to_bytes());
    
    // 签名第三个输入（Taproot）
    let prevouts = amounts.iter().zip(utxos_script_pubkeys.iter())
        .map(|(amount, script)| TxOut {
            value: *amount,
            script_pubkey: script.clone(),
        })
        .collect::<Vec<_>>();
    
    let sighash3 = SighashCache::new(&tx).taproot_key_spend_signature_hash(
        2,
        &bitcoin::sighash::Prevouts::All(&prevouts),
        TapSighashType::Default,
    )?;
    
    let message3 = Message::from_digest_slice(&sighash3[..])?;
    let signature3 = secp.sign_schnorr_no_aux_rand(&message3, &keypair);
    
    // 为Taproot输入设置witness
    tx.input[2].witness.push(&signature3.as_ref());
    
    println!("\n签名后交易: {}", hex::encode(bitcoin::consensus::serialize(&tx)));
    println!("\nTxId: {}", tx.txid());
    println!("TxwId: {}", tx.wtxid());
    println!("交易大小: {} bytes", tx.total_size());
    println!("虚拟大小: {} vbytes", tx.vsize());
    
    // 重新计算手续费
    let new_fee = Amount::from_sat((tx.vsize() as f64 * 1.05) as u64);
    println!("重新计算手续费: {} satoshi", new_fee.to_sat());
    
    // 重新创建交易输出
    let new_output_amount = total_input - new_fee;
    let new_txout = TxOut {
        value: new_output_amount,
        script_pubkey: to_address.script_pubkey(),
    };
    
    // 重新创建交易
    let mut final_tx = Transaction {
        version: Version::TWO,
        lock_time: LockTime::ZERO,
        input: vec![
            TxIn {
                previous_output: OutPoint {
                    txid: Txid::from_str(txid1)?,
                    vout: vout1,
                },
                script_sig: ScriptBuf::new(),
                sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
                witness: Witness::new(),
            },
            TxIn {
                previous_output: OutPoint {
                    txid: Txid::from_str(txid2)?,
                    vout: vout2,
                },
                script_sig: ScriptBuf::new(),
                sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
                witness: Witness::new(),
            },
            TxIn {
                previous_output: OutPoint {
                    txid: Txid::from_str(txid3)?,
                    vout: vout3,
                },
                script_sig: ScriptBuf::new(),
                sequence: bitcoin::Sequence::ENABLE_RBF_NO_LOCKTIME,
                witness: Witness::new(),
            },
        ],
        output: vec![new_txout],
    };
    
    // 重新签名所有输入
    // Legacy输入
    let final_sighash1 = SighashCache::new(&final_tx).legacy_signature_hash(
        0,
        &script_pubkey1,
        EcdsaSighashType::All.to_u32(),
    )?;
    let final_message1 = Message::from_digest_slice(&final_sighash1[..])?;
    let final_signature1 = secp.sign_ecdsa(&final_message1, &private_key.inner);
    let mut final_sig1_bytes = final_signature1.serialize_der().to_vec();
    final_sig1_bytes.push(EcdsaSighashType::All.to_u32() as u8);
    
    let final_sig1_push = PushBytesBuf::try_from(final_sig1_bytes.clone()).unwrap();
    let final_pubkey1_push = PushBytesBuf::try_from(public_key.to_bytes()).unwrap();
    final_tx.input[0].script_sig = ScriptBuf::builder()
        .push_slice(&final_sig1_push)
        .push_slice(&final_pubkey1_push)
        .into_script();
    
    // SegWit输入
    let final_sighash2 = SighashCache::new(&final_tx).p2wpkh_signature_hash(
        1,
        &segwit_script_pubkey,
        amount2,
        EcdsaSighashType::All,
    )?;
    let final_message2 = Message::from_digest_slice(&final_sighash2[..])?;
    let final_signature2 = secp.sign_ecdsa(&final_message2, &private_key.inner);
    let mut final_sig2_bytes = final_signature2.serialize_der().to_vec();
    final_sig2_bytes.push(EcdsaSighashType::All.to_u32() as u8);
    
    final_tx.input[1].witness.push(&final_sig2_bytes);
    final_tx.input[1].witness.push(&public_key.to_bytes());
    
    // Taproot输入
    let final_prevouts = amounts.iter().zip(utxos_script_pubkeys.iter())
        .map(|(amount, script)| TxOut {
            value: *amount,
            script_pubkey: script.clone(),
        })
        .collect::<Vec<_>>();
    
    let final_sighash3 = SighashCache::new(&final_tx).taproot_key_spend_signature_hash(
        2,
        &bitcoin::sighash::Prevouts::All(&final_prevouts),
        TapSighashType::Default,
    )?;
    
    let final_message3 = Message::from_digest_slice(&final_sighash3[..])?;
    let final_signature3 = secp.sign_schnorr_no_aux_rand(&final_message3, &keypair);
    
    final_tx.input[2].witness.push(&final_signature3.as_ref());
    
    let final_signed_tx_hex = hex::encode(bitcoin::consensus::serialize(&final_tx));
    
    println!("\nTxId: {}", final_tx.txid());
    println!("TxwId: {}", final_tx.wtxid());
    println!("交易大小: {} bytes", final_tx.total_size());
    println!("虚拟大小: {} vbytes", final_tx.vsize());
    println!("\n最终签名交易: {}", final_signed_tx_hex);
    
    // 广播交易
    println!("\n=== 广播交易 ===");
    let mempool_api = "https://mempool.space/testnet/api/tx";
    
    match reqwest::Client::new()
        .post(mempool_api)
        .body(final_signed_tx_hex.clone())
        .send()
        .await
    {
        Ok(response) => {
            if response.status().is_success() {
                let txid = response.text().await?;
                println!("交易成功！");
                println!("交易ID: {}", txid);
                println!("查看交易: https://mempool.space/testnet/tx/{}", txid);
            } else {
                let error_text = response.text().await?;
                println!("广播失败: {}", error_text);
            }
        }
        Err(e) => {
            println!("错误: {}", e);
        }
    }

    Ok(())
}