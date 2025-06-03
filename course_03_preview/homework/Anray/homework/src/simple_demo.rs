use bitcoin::{
    key::Keypair,
    script::Builder,
    secp256k1::{All, Secp256k1},
    Network, ScriptBuf, XOnlyPublicKey,
};

// 使用操作码常量
use bitcoin::blockdata::opcodes::all::*;
use bitcoin::blockdata::opcodes::all::OP_PUSHNUM_1 as OP_1;
use secp256k1::rand;
use sha2::{Digest, Sha256};
use hex;

/// 简化的 Taproot 演示
pub struct SimpleTaprootDemo {
    network: Network,
    secp: Secp256k1<All>,
}

impl SimpleTaprootDemo {
    /// 创建新的演示实例
    pub fn new(network: Network) -> Self {
        Self {
            network,
            secp: Secp256k1::new(),
        }
    }

    /// 创建密码验证脚本
    fn create_password_script(&self, password: &str) -> ScriptBuf {
        let mut hasher = Sha256::new();
        hasher.update(password.as_bytes());
        let password_hash = hasher.finalize();
        let hash_bytes: [u8; 32] = password_hash.into();
        
        Builder::new()
            .push_opcode(OP_SHA256)
            .push_slice(&hash_bytes)
            .push_opcode(OP_EQUALVERIFY)
            .push_opcode(OP_1)
            .into_script()
    }

    /// 创建时间锁脚本
    fn create_timelock_script(&self, blocks: u32) -> ScriptBuf {
        Builder::new()
            .push_int(blocks as i64)
            .push_opcode(OP_NOP)
            .push_opcode(OP_DROP)
            .push_opcode(OP_1)
            .into_script()
    }

    /// 创建多重签名脚本
    fn create_multisig_script(&self, pubkey1: &XOnlyPublicKey, pubkey2: &XOnlyPublicKey) -> ScriptBuf {
        Builder::new()
            .push_x_only_key(pubkey1)
            .push_opcode(OP_CHECKSIG)
            .push_x_only_key(pubkey2)
            .push_opcode(OP_CHECKSIGADD)
            .push_int(2)
            .push_opcode(OP_EQUAL)
            .into_script()
    }

    /// 演示脚本创建
    pub fn demonstrate_script_creation(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("\n🏗️  Taproot 脚本创建演示");
        println!("{}", "-".repeat(30));

        // 生成密钥
        let internal_key = Keypair::new(&self.secp, &mut rand::thread_rng());
        let internal_pubkey = XOnlyPublicKey::from_keypair(&internal_key).0;
        
        let key1 = Keypair::new(&self.secp, &mut rand::thread_rng());
        let key2 = Keypair::new(&self.secp, &mut rand::thread_rng());
        let pubkey1 = XOnlyPublicKey::from_keypair(&key1).0;
        let pubkey2 = XOnlyPublicKey::from_keypair(&key2).0;
        
        println!("🔑 生成的密钥:");
        println!("   📍 内部公钥: {}", hex::encode(internal_pubkey.serialize()));
        println!("   👤 用户1公钥: {}", hex::encode(pubkey1.serialize()));
        println!("   👤 用户2公钥: {}", hex::encode(pubkey2.serialize()));

        // 创建脚本
        let password_script = self.create_password_script("bitcoin2025");
        let timelock_script = self.create_timelock_script(144);
        let multisig_script = self.create_multisig_script(&pubkey1, &pubkey2);

        println!("\n📜 创建的脚本:");
        println!("   🔐 密码脚本: {} 字节", password_script.len());
        println!("      内容: {}", password_script);
        println!("   ⏰ 时间锁脚本: {} 字节", timelock_script.len());
        println!("      内容: {}", timelock_script);
        println!("   👥 多重签名脚本: {} 字节", multisig_script.len());
        println!("      内容: {}", multisig_script);
        
        Ok(())
    }

    /// 演示 Key Path 花费
    pub fn demonstrate_key_path(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("\n🔑 Key Path 花费演示");
        println!("{}", "-".repeat(25));
        
        // 生成内部密钥
        let internal_key = Keypair::new(&self.secp, &mut rand::thread_rng());
        let internal_pubkey = XOnlyPublicKey::from_keypair(&internal_key).0;
        
        println!("📍 内部公钥: {}", hex::encode(internal_pubkey.serialize()));
        
        Ok(())
    }
    
    /// 演示 Script Path 花费
    pub fn demonstrate_script_path(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("\n📜 Script Path 花费演示");
        println!("{}", "-".repeat(28));
        
        // 创建示例脚本
        let password_script = self.create_password_script("bitcoin2025");
        
        println!("🔐 使用密码脚本进行花费:");
        println!("   脚本内容: {}", password_script);
        println!("   脚本大小: {} 字节", password_script.len());
        
        Ok(())
    }

    pub fn run_demo(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("🎯 Taproot Script Path 交易完整演示");
        println!("{}", "=".repeat(40));
        
        self.demonstrate_script_creation()?;
        self.demonstrate_key_path()?;
        self.demonstrate_script_path()?;
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_demo_creation() {
        let demo = SimpleTaprootDemo::new(Network::Testnet);
        assert_eq!(demo.network, Network::Testnet);
    }

    #[test]
    fn test_password_script_creation() {
        let demo = SimpleTaprootDemo::new(Network::Testnet);
        let script = demo.create_password_script("test123");
        assert!(!script.is_empty());
    }

    #[test]
    fn test_timelock_script_creation() {
        let demo = SimpleTaprootDemo::new(Network::Testnet);
        let script = demo.create_timelock_script(144);
        assert!(!script.is_empty());
    }
}