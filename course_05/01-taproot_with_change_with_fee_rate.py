import logging
from utils.tx_creator import create_taproot_tx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 交易参数
    sender_private_key = "cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT"
    recipient_addr = "tb1pezpnfztmzltyvke55cwqc206vdyz8chz4w52yrd8w4ah402jqu2qv9hdkg"
    amount_to_send = 0.00001000  # BTC
    fee_rate = 2.0  # sat/vB
    
    try:
        # 创建交易
        signed_tx, tx_details = create_taproot_tx(
            sender_private_key=sender_private_key,
            recipient_addr=recipient_addr,
            amount_to_send=amount_to_send,
            fee_rate=fee_rate
        )
        
        # 打印交易信息
        print("\n最终交易详情:")
        print("=" * 50)
        print(f"交易ID: {tx_details['txid']}")
        print(f"交易大小: {tx_details['tx_size']} bytes")
        print(f"虚拟大小: {tx_details['tx_vsize']} vbytes")
        print("\n金额详情:")
        print(f"发送金额: {tx_details['amount_sats']} 聪 ({tx_details['amount']:.8f} BTC)")
        print(f"找零金额: {tx_details['change_amount_sats']} 聪 ({tx_details['change_amount']:.8f} BTC)")
        print(f"手续费: {tx_details['fee_sats']} 聪 ({tx_details['fee']:.8f} BTC)")
        print("\n签名后的交易:")
        print(signed_tx)
        print("\n您可以在这里广播交易:")
        print("https://mempool.space/testnet/tx/push")
        
    except Exception as e:
        logger.error(f"交易创建失败: {e}")
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 