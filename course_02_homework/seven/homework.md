# 课后作业：

1. 观察legacy、segwit和taproot 地址的长短，说说他们有什么区别
2. 观察legacy、segwit和taproot 锁定脚本（scriptpubkey)的长短，说说他们有什么区别
3. 动手编写：segwit到legacy地址的代码；taproot到segwit、legacy地址的代码
4. 动手编写：加难度，构建一个交易，输入是三种地址（legacy、segwit、taproot），分别取其UTXO，然后支付给一个地址，预估手续费，并把 *输入金额-手续费 作为需要支付出去的金额。*注意签名的方法。