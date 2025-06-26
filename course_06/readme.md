## **1、 很快介绍一下Ordinal 协议和 Brc20协议原理**

参考文章：https://www.techflowpost.com/article/detail_16179.html

如何在比特币上附加信息：https://mempool.space/tx/4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

https://mempool.space/tx/cb01ea705494ce66d7e5b7cb51bb5b39b8e8ce31e168d1bd7dda253af359cc77

<aside>
💡

全节点复习、Ord服务器的安装、Ord和全节点的互动

</aside>

## **2、演示一下如何在Ord客户端Deploy和Mint Brc20，文字、以及NFT**

<aside>
💡

命令行方式、代码RPC方式（作业）、Unisat钱包的方式

</aside>

BRC20：https://mempool.space/testnet/tx/a48443b3b4427c72a9a2e3d1fcf302a471059a14712e7a304fd22d2532b82056

NFT:https://mempool.space/tx/e7454db518ca3910d2f17f41c7b215d6cba00f29bd186ae77d4fcd7f0ba7c0e1

## **3、解析浏览器上的链上数据，跟我们熟悉的Taproot Commit/Reveal模式的进行分析**

<aside>
💡

——P2KH+附属数据、单叶子节点

——大胆猜测：我们可以自己构建commit、然后自己reveal

——测试我们的猜想

——再测试Reveal模式

</aside>

对HEX的解析：见tools里面的hex_to_string

对图片的解析-见Claude编写的解析器

## **4、作业：**

——下载Ord Server，并和自己的全节点通讯、索引，用代码RPC的方式去通讯，做一些常规的查询操作；

——用代码的方式去发布自己的NFT(需要提交测试成功的代码！）

——自学递归Ordinal铭文，并发布一个有创造性格式的铭文
