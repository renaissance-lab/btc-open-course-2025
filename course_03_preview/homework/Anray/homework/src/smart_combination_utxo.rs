//! 智能UTXO选择器
//!
//! 该程序用于从一个地址的多个UTXO中智能选择合适的组合来满足指定的交易金额。
//! 支持多种UTXO选择策略：
//! 1. 贪心算法：优先选择最大的UTXO
//! 2. 最小变化算法：尽量选择接近目标金额的UTXO组合，减少找零
//! 3. 合并小额UTXO：优先选择小额UTXO，帮助清理钱包
//!
//! 使用方法:
//! cargo run -- <地址> <目标金额> [--strategy <选择策略>] [--network <网络>]

use anyhow::{anyhow, Result};
use clap::{Parser, ValueEnum};
use reqwest::Client;
use rust_decimal::Decimal;
use rust_decimal::prelude::ToPrimitive;
use serde::{Deserialize, Serialize};
use std::str::FromStr;

const BASE_URL: &str = "https://mempool.space";
const SATOSHI_PER_BTC: u64 = 100_000_000;

#[derive(Debug, Clone, ValueEnum)]
enum Strategy {
    /// 贪心算法：优先选择最大的UTXO
    Greedy,
    /// 最小变化算法：尽量选择接近目标金额的UTXO组合
    MinChange,
    /// 合并小额UTXO：优先选择小额UTXO，帮助清理钱包
    Consolidate,
}

#[derive(Parser)]
#[command(name = "smart-utxo-selector")]
#[command(about = "智能UTXO选择器")]
struct Args {
    /// 比特币地址
    address: String,
    /// 目标金额（BTC）
    amount: f64,
    /// UTXO选择策略
    #[arg(short, long, default_value = "greedy")]
    strategy: Strategy,
    /// 比特币网络
    #[arg(short, long, default_value = "testnet")]
    network: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
struct Utxo {
    txid: String,
    vout: u32,
    value: u64,
}

#[derive(Debug, Deserialize, Serialize)]
struct FeeEstimate {
    #[serde(rename = "fastestFee")]
    fastest_fee: Option<u32>,
    #[serde(rename = "halfHourFee")]
    half_hour_fee: Option<u32>,
    #[serde(rename = "hourFee")]
    hour_fee: Option<u32>,
    #[serde(rename = "economyFee")]
    economy_fee: Option<u32>,
    #[serde(rename = "minimumFee")]
    minimum_fee: Option<u32>,
}

#[derive(Debug, Serialize)]
struct TransactionInput {
    txid: String,
    vout: u32,
    value: u64,
}

#[derive(Debug, Serialize)]
struct TransactionTemplate {
    inputs: Vec<TransactionInput>,
    outputs: Vec<String>, // 占位符，用户需要填写实际输出
}

struct SmartUtxoSelector {
    client: Client,
    network: String,
    base_url: String,
}

impl SmartUtxoSelector {
    fn new(network: String) -> Self {
        let base_url = if network == "mainnet" {
            BASE_URL.to_string()
        } else {
            format!("{}/{}", BASE_URL, network)
        };
        
        Self {
            client: Client::new(),
            network,
            base_url,
        }
    }

    async fn get_utxos(&self, address: &str) -> Result<Vec<Utxo>> {
        let url = format!("{}/api/address/{}/utxo", self.base_url, address);
        let response = self.client.get(&url).send().await?;
        
        if !response.status().is_success() {
            return Err(anyhow!(
                "获取UTXO失败: {} {}",
                response.status(),
                response.text().await?
            ));
        }
        
        let utxos: Vec<Utxo> = response.json().await?;
        
        println!("地址 {} 的UTXO列表:", address);
        for (i, utxo) in utxos.iter().enumerate() {
            println!(
                "  UTXO #{}: {}:{} - {} satoshis",
                i + 1,
                utxo.txid,
                utxo.vout,
                utxo.value
            );
        }
        
        Ok(utxos)
    }

    fn select_utxos_greedy(&self, utxos: &[Utxo], target_amount: u64) -> Result<(Vec<Utxo>, u64)> {
        let mut sorted_utxos = utxos.to_vec();
        sorted_utxos.sort_by(|a, b| b.value.cmp(&a.value));
        
        let mut selected_utxos = Vec::new();
        let mut total_selected = 0u64;
        
        for utxo in sorted_utxos {
            if total_selected >= target_amount {
                break;
            }
            selected_utxos.push(utxo.clone());
            total_selected += utxo.value;
        }
        
        if total_selected < target_amount {
            return Err(anyhow!(
                "UTXO总额不足，需要{}，仅有{}",
                target_amount,
                total_selected
            ));
        }
        
        Ok((selected_utxos, total_selected))
    }

    fn select_utxos_min_change(&self, utxos: &[Utxo], target_amount: u64) -> Result<(Vec<Utxo>, u64)> {
        // 首先检查是否有单个UTXO接近目标值
        for utxo in utxos {
            if utxo.value >= target_amount {
                return Ok((vec![utxo.clone()], utxo.value));
            }
        }
        
        // 使用动态规划找到最优组合
        let target = target_amount as usize;
        
        // dp[i] 表示金额i是否可达
        let mut dp = vec![false; target + 1];
        dp[0] = true;
        
        // parent[i] 记录达到金额i使用的UTXO索引
        let mut parent: Vec<Option<usize>> = vec![None; target + 1];
        
        for (utxo_idx, utxo) in utxos.iter().enumerate() {
            let value = utxo.value as usize;
            for j in (value..=target).rev() {
                if dp[j - value] && !dp[j] {
                    dp[j] = true;
                    parent[j] = Some(utxo_idx);
                }
            }
        }
        
        // 寻找满足条件的最小组合
        for amount in target..dp.len() {
            if dp[amount] {
                let mut selected_indices = Vec::new();
                let mut current = amount;
                
                while let Some(utxo_idx) = parent[current] {
                    selected_indices.push(utxo_idx);
                    current -= utxos[utxo_idx].value as usize;
                }
                
                let selected_utxos: Vec<Utxo> = selected_indices
                    .into_iter()
                    .map(|idx| utxos[idx].clone())
                    .collect();
                
                let total_value: u64 = selected_utxos.iter().map(|u| u.value).sum();
                return Ok((selected_utxos, total_value));
            }
        }
        
        // 如果没有找到精确匹配，使用贪心算法
        self.select_utxos_greedy(utxos, target_amount)
    }

    fn select_utxos_consolidate(&self, utxos: &[Utxo], target_amount: u64) -> Result<(Vec<Utxo>, u64)> {
        let mut sorted_utxos = utxos.to_vec();
        sorted_utxos.sort_by(|a, b| a.value.cmp(&b.value));
        
        let mut selected_utxos = Vec::new();
        let mut total_selected = 0u64;
        
        for utxo in sorted_utxos {
            selected_utxos.push(utxo.clone());
            total_selected += utxo.value;
            if total_selected >= target_amount {
                break;
            }
        }
        
        if total_selected < target_amount {
            return Err(anyhow!(
                "UTXO总额不足，需要{}，仅有{}",
                target_amount,
                total_selected
            ));
        }
        
        Ok((selected_utxos, total_selected))
    }

    async fn select_utxos(
        &self,
        address: &str,
        target_amount: u64,
        strategy: &Strategy,
    ) -> Result<(Vec<Utxo>, u64)> {
        let utxos = self.get_utxos(address).await?;
        
        if utxos.is_empty() {
            return Err(anyhow!("地址 {} 没有可用的UTXO", address));
        }
        
        println!("使用 {:?} 策略选择UTXO", strategy);
        
        match strategy {
            Strategy::Greedy => self.select_utxos_greedy(&utxos, target_amount),
            Strategy::MinChange => self.select_utxos_min_change(&utxos, target_amount),
            Strategy::Consolidate => self.select_utxos_consolidate(&utxos, target_amount),
        }
    }

    fn create_transaction_input_template(&self, selected_utxos: &[Utxo]) -> String {
        let inputs: Vec<TransactionInput> = selected_utxos
            .iter()
            .map(|utxo| TransactionInput {
                txid: utxo.txid.clone(),
                vout: utxo.vout,
                value: utxo.value,
            })
            .collect();
        
        let template = TransactionTemplate {
            inputs,
            outputs: vec!["// 请在这里添加您的输出".to_string()],
        };
        
        serde_json::to_string_pretty(&template).unwrap_or_else(|_| "JSON序列化失败".to_string())
    }

    async fn get_fee_estimate(&self) -> Result<FeeEstimate> {
        let url = format!("{}/api/v1/fees/recommended", self.base_url);
        let response = self.client.get(&url).send().await?;
        
        if !response.status().is_success() {
            return Err(anyhow!(
                "获取费率失败: {} {}",
                response.status(),
                response.text().await?
            ));
        }
        
        Ok(response.json().await?)
    }

    fn estimate_tx_size(&self, input_count: usize, output_count: usize) -> usize {
        // 简化的交易大小估计（假设P2WPKH输入和输出）
        let base_size = 10; // 版本 + 锁定时间
        let input_weight = 41 * 4; // P2WPKH输入的权重单位
        let output_weight = 31 * 4; // P2WPKH输出的权重单位
        
        let total_weight = base_size * 4 + input_count * input_weight + output_count * output_weight;
        (total_weight + 3) / 4 // 向上取整到最接近的整数
    }

    async fn estimate_fee(&self, input_count: usize, output_count: usize, fee_rate: Option<u32>) -> Result<u64> {
        let fee_rate = if let Some(rate) = fee_rate {
            rate
        } else {
            let fee_estimates = self.get_fee_estimate().await?;
            fee_estimates.hour_fee.unwrap_or(10) // 默认使用hourFee，如果没有则使用10 sat/vB
        };
        
        let tx_size = self.estimate_tx_size(input_count, output_count);
        Ok(tx_size as u64 * fee_rate as u64)
    }
}

fn btc_to_satoshi(btc_amount: f64) -> u64 {
    (Decimal::from_str(&btc_amount.to_string()).unwrap() * Decimal::from(SATOSHI_PER_BTC))
        .to_u64()
        .unwrap_or(0)
}

fn satoshi_to_btc(satoshi_amount: u64) -> f64 {
    (Decimal::from(satoshi_amount) / Decimal::from(SATOSHI_PER_BTC))
        .to_f64()
        .unwrap_or(0.0)
}

pub async fn smart_combination_utxos() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    
    // 将BTC转换为satoshi
    let target_satoshis = btc_to_satoshi(args.amount);
    
    let selector = SmartUtxoSelector::new(args.network.clone());
    
    // 获取费率估计
    match selector.get_fee_estimate().await {
        Ok(fee_estimates) => {
            println!("当前费率估计: {}", serde_json::to_string_pretty(&fee_estimates)?);
        }
        Err(e) => {
            println!("获取费率估计失败: {}", e);
        }
    }
    
    // 选择UTXO
    let (selected_utxos, total_value) = selector
        .select_utxos(&args.address, target_satoshis, &args.strategy)
        .await?;
    
    // 估计费用
    let estimated_fee = selector.estimate_fee(selected_utxos.len(), 2, None).await?;
    
    // 计算找零
    let change = total_value.saturating_sub(target_satoshis + estimated_fee);
    
    println!("\n=== 选择结果 ===");
    println!(
        "目标金额: {} BTC ({} satoshis)",
        args.amount, target_satoshis
    );
    println!("选择的UTXO数量: {}", selected_utxos.len());
    println!(
        "选择的UTXO总价值: {:.8} BTC ({} satoshis)",
        satoshi_to_btc(total_value),
        total_value
    );
    println!(
        "估计费用: {:.8} BTC ({} satoshis)",
        satoshi_to_btc(estimated_fee),
        estimated_fee
    );
    println!(
        "找零金额: {:.8} BTC ({} satoshis)",
        satoshi_to_btc(change),
        change
    );
    
    println!("\n=== 选择的UTXO详情 ===");
    for (i, utxo) in selected_utxos.iter().enumerate() {
        println!(
            "UTXO #{}: {}:{} - {:.8} BTC ({} satoshis)",
            i + 1,
            utxo.txid,
            utxo.vout,
            satoshi_to_btc(utxo.value),
            utxo.value
        );
    }
    
    println!("\n=== 交易输入模板 ===");
    println!("{}", selector.create_transaction_input_template(&selected_utxos));

    Ok(())
}