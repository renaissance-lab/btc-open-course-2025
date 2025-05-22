-  1. 观察legacy、segwit和taproot 地址的⻓短，说说他们有什么区别

    - Legacy地址
        - 25字节
        - 34个字符
        - 前缀
            - 主网：1
            - 测试网：m

    - SegWit地址
        - 21字节
        - 42~46个字符
        - 前缀
            - 主网：bc1q
            - 测试网：tb1q
    - Taproot地址
        - 33字节
        - 58~62个字符
        - 前缀
            - 主网：bc1p
            - 测试网：tb1p

    > 结论：Legacy地址最短，Taproot地址最长，SegWit地址介于两者之间。


    ```
    # 举例：

    P2PKH 地址(Legacy): mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1
    P2WPKH 地址(SegWit): tb1qq2x3nt3zzqz7rxgxf03m4tj5eckywehaklggph
    P2TR 地址(Taproot): tb1p9q80mtqns48e8dm4gkuq0n5tx9zdwqqqh9skyagqrtq3q7jvdqfqe02xas

    ```

-  2. 观察legacy、segwit和taproot 锁定脚本（scriptpubkey）的⻓短，说说他们有什么区别

    - Legacy (P2PKH) 锁定脚本：
        - 脚本格式：OP_DUP OP_HASH160 <20字节公钥哈希> OP_EQUALVERIFY OP_CHECKSIG
        - 十六进制表示：76a914{20字节哈希}88ac
        - 脚本长度：25 字节
        - 操作码数量：5个操作码 + 数据
    - SegWit (P2WPKH) 锁定脚本：
        - 脚本格式：OP_0 <20字节公钥哈希>
        - 十六进制表示：0014{20字节哈希}
        - 脚本长度：22 字节
        - 操作码数量：1个操作码 + 数据
    - Taproot (P2TR) 锁定脚本：
        - 脚本格式：OP_1 <32字节x-only公钥>
        - 十六进制表示：5120{32字节公钥}
        - 脚本长度：34 字节
        - 操作码数量：1个操作码 + 数据

    > 结论：
    > 1. SegWit 锁定脚本最短，Taproot 锁定脚本最长，Legacy 锁定脚本介于两者之间。
    > 2. Legacy 锁定脚本最复杂，SegWit 和 Taproot 锁定脚本结构简单，只有一个操作码和数据。

