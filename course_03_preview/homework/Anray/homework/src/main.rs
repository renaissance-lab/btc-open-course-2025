mod simple_demo;

use simple_demo::SimpleTaprootDemo;
use bitcoin::Network;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 启动 Taproot Script Path 交易演示");
    println!("{}", "=".repeat(50));
    
    let demo = SimpleTaprootDemo::new(Network::Testnet);
    demo.run_demo()?;
    
    Ok(())
}
