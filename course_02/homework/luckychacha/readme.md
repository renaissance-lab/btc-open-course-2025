-  观察legacy、segwit和taproot 地址的⻓短，说说他们有什么区别

举例：
P2PKH 地址(Legacy): mfkSgFzcijcub1AXuvLMhHbXY5Wodyy5z1
P2WPKH 地址(SegWit): tb1qq2x3nt3zzqz7rxgxf03m4tj5eckywehaklggph
P2TR 地址(Taproot): tb1p9q80mtqns48e8dm4gkuq0n5tx9zdwqqqh9skyagqrtq3q7jvdqfqe02xas

Legacy地址
    - 25字节
    - 34个字符
    - 前缀
        - 主网：1
        - 测试网：m

SegWit地址
    - 21字节
    - 42~46个字符
    - 前缀
        - 主网：bc1q
        - 测试网：tb1q
Taproot地址
    - 33字节
    - 58~62个字符
    - 前缀
        - 主网：bc1p
        - 测试网：tb1p
        
结论：Legacy地址最短，Taproot地址最长，SegWit地址介于两者之间。

-  观察legacy、segwit和taproot 锁定脚本（scriptpubkey)的⻓短，说说他们有什么区别