import hashlib

class TransactionAnalyzer:
    @staticmethod
    def hash256(data):
        """双重 SHA256 哈希"""
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()
    
    def build_tx_with_sig(self, signature):
        """使用指定签名构建交易"""
        tx = b""
        
        # 版本号
        tx += (1).to_bytes(4, 'little')
        
        # 输入数量
        tx += b"\x01"
        
        # 输入
        tx += bytes(32)  # 前一个交易哈希
        tx += (0).to_bytes(4, 'little')  # 输出索引
        
        # ScriptSig
        pubkey = bytes.fromhex("021d85b17a74b2a1cf2152907c908ea1e5d38616f1f1c345af75d23c38b3ad4449")
        script_sig = signature + pubkey
        tx += len(script_sig).to_bytes(1, 'big')
        tx += script_sig
        
        tx += (0xffffffff).to_bytes(4, 'little')  # Sequence
        
        # 输出数量
        tx += b"\x01"
        
        # 输出
        tx += (1200).to_bytes(8, 'little')  # 金额
        script_pubkey = bytes.fromhex("76a9143517d46b972af88b6064090cfb44e346df0fbab188ac")
        tx += len(script_pubkey).to_bytes(1, 'big')
        tx += script_pubkey
        
        # Locktime
        tx += (0).to_bytes(4, 'little')
        
        return tx

class SegWitVsLegacyDemo:
    def __init__(self):
        self.analyzer = TransactionAnalyzer()
    
    def build_segwit_tx(self, witness_data):
        """构建 SegWit 交易（用于 TXID 计算）"""
        tx = b""
        
        # 版本号
        tx += (1).to_bytes(4, 'little')
        
        # 输入数量（不包含 marker 和 flag）
        tx += b"\x01"
        
        # 输入
        tx += bytes(32)  # 前一个交易哈希
        tx += (0).to_bytes(4, 'little')  # 输出索引
        tx += b"\x00"  # ScriptSig 长度为 0
        tx += (0xffffffff).to_bytes(4, 'little')  # Sequence
        
        # 输出数量
        tx += b"\x01"
        
        # 输出
        tx += (800).to_bytes(8, 'little')  # 金额
        script_pubkey = bytes.fromhex("0014163177c0585515fd30b8b605155953b4007e5767")
        tx += len(script_pubkey).to_bytes(1, 'big')
        tx += script_pubkey
        
        # Locktime
        tx += (0).to_bytes(4, 'little')
        
        return tx
    
    def demonstrate_segwit_immunity(self):
        """演示 SegWit 对延展性的免疫"""
        # 原始见证数据
        original_witness = "304402200778ccde1fdc101b39a959f53ce04eb995b08a2459388ba087b3e873f75aa224a02206d6b8021b189c3a095e4c51e3da3d612994f4780a4ef1f0df3838dd10451b59801"
        
        # 修改见证数据（改变最后一个字节）
        modified_witness = original_witness[:-2] + "02"
        
        print("=== SegWit 交易延展性测试 ===")
        print(f"原始见证数据: ...{original_witness[-10:]}")
        print(f"修改后见证数据: ...{modified_witness[-10:]}")
        
        # 注意：SegWit TXID 计算不包含见证数据
        tx1 = self.build_segwit_tx(original_witness)
        tx2 = self.build_segwit_tx(modified_witness)
        
        txid1 = self.analyzer.hash256(tx1)[::-1].hex()
        txid2 = self.analyzer.hash256(tx2)[::-1].hex()
        
        print(f"\n原始 TXID: {txid1}")
        print(f"修改后 TXID: {txid2}")
        print(f"TXID 是否改变: {txid1 != txid2}")
        print("\n注意：TXID 保持不变！这就是 SegWit 的威力！")
    
    def demonstrate_legacy_malleability(self):
        """演示 Legacy 交易的延展性"""
        # 原始签名
        original_sig = "304402204a6e0e3a075009bf4e699cf255333e58e9a9443193a9c6a0b6ad4e01775e05ac02206943f7c3c2b6caa2781cb5af454659d7ae2183f7aed6587a03b5c582699805cd01"
        
        # 修改签名（改变最后一个字节）
        modified_sig = original_sig[:-2] + "02"
        
        print("\n=== Legacy 交易延展性测试 ===")
        print(f"原始签名: ...{original_sig[-10:]}")
        print(f"修改后签名: ...{modified_sig[-10:]}")
        
        # Legacy 交易包含签名在 TXID 计算中
        tx1 = self.analyzer.build_tx_with_sig(bytes.fromhex(original_sig))
        tx2 = self.analyzer.build_tx_with_sig(bytes.fromhex(modified_sig))
        
        txid1 = self.analyzer.hash256(tx1)[::-1].hex()
        txid2 = self.analyzer.hash256(tx2)[::-1].hex()
        
        print(f"\n原始 TXID: {txid1}")
        print(f"修改后 TXID: {txid2}")
        print(f"TXID 是否改变: {txid1 != txid2}")
        print("\n注意：TXID 改变了！这就是交易延展性问题！")
    
    def compare_both(self):
        """对比 Legacy 和 SegWit 的延展性行为"""
        print("=" * 50)
        print("交易延展性对比实验")
        print("=" * 50)
        
        self.demonstrate_legacy_malleability()
        print("\n" + "-" * 50)
        self.demonstrate_segwit_immunity()
        
        print("\n" + "=" * 50)
        print("总结：")
        print("1. Legacy 交易：修改签名会改变 TXID")
        print("2. SegWit 交易：修改见证数据不会改变 TXID")
        print("3. 这就是为什么 SegWit 能支持闪电网络等高级应用")
        print("=" * 50)

# 运行完整的对比演示
if __name__ == "__main__":
    demo = SegWitVsLegacyDemo()
    demo.compare_both()