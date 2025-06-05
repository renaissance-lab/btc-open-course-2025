mod legacy_segwit_taproot_to_legacy;
mod segwit_to_legacy;
mod taproot_to_legacy_segwit;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    legacy_segwit_taproot_to_legacy::legacy_segwit_taproot_to_legacy().await?;
    segwit_to_legacy::segwit_to_legacy().await?;
    taproot_to_legacy_segwit::taproot_to_legacy_segwit().await?;
    
    Ok(())
}
