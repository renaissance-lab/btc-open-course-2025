# **课前**

1、学习bitcoin coding是对2万亿美元的资产的尽调

2、比特币全节点和钱包配置

3、预习的基本知识概要

# **课程目录**

1、UTXO和转账

2、脚本验证执行过程

3、legacy、segwit、taproot的演变和编程实践

# **课程的内容**

## 1、UTXO的基本概念

浏览器举例

钱包举例

- *一个地址有多笔交易、多个UTXO、有余额*
- 一个地址对应一个私钥（私钥-公钥-地址的导出关系）
- 一个助记词对应无数地址（Sparrow)

## 2、转账的本质



malleability 



## 3、编程实践：

先建一个地址

实现从一个地址到另外一个地址的转账

在这个过程中介绍segwit和taproot的原理

## 4、课后作业：

—观察legacy、segwit和taproot 地址的长短，说说他们有什么区别

—观察legacy、segwit和taproot 锁定脚本（scriptpubkey)的长短，说说他们有什么区别

—动手编写：segwit到legacy地址的代码；taproot到segwit、legacy地址的代码

—动手编写：加难度，构建一个交易，输入是三种地址（legacy、segwit、taproot），分别取其UTXO，然后支付给一个地址，预估手续费，并把 *输入金额-手续费 作为需要支付出去的金额。*注意签名的方法。
