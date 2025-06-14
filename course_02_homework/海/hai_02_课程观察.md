#### 1. 观察legacy、segwit和taproot 地址的长短，说说他们有什么区别

>  私钥（WIF）：cVgbLBMymtebKVGoriSVWxEBahbGvvx3tuKJftGpaJBcfjujZd4C
>
>  公钥（HEX）：02791c756a773e606ab0e05dbdb453dec465d0796b94ceb536a2fa19ddca9efef4
>
>  === 不同类型的地址 ===  
>
>  传统Legacy地址: n4juXXS637FKJy9zJsbrCbTLvdQLRZCjST
>
>  SegWit地址: tb1ql67l67sy6zn6d2ztf75chu3h498ydupplwscpt
>
>  Taproot地址: tb1p484vwajatgstnx82fssqtprljpj9g3ruzj9h8hx03sjnggjcpxesjzzjpg



1）传统地址（P2PKH),主网以1开头，测试网以 m或n 开头，使用Base58Check编码，长度34个字符左右  ；

2）SegWit地址（P2WPKH)，主网以bc1开头，测试网以tb1开头，使用Bech32编码，长度42个字符左右  ；

3）Taproot地址（P2TR): 主网以bc1开头, 测试网以tb1开头，使用Bech32编码，长度62个字符左右  。



#### 2. 观察legacy、segwit和taproot 锁定脚本（scriptpubkey)的长短，说说他们有什么区别

> Legacy锁定脚本: ['OP_DUP', 'OP_HASH160', 'cd040de1a07381fe759df9fe8e34e5218ac72a4a', 'OP_EQUALVERIFY', 'OP_CHECKSIG']  
>
> SegWit锁定脚本: ['OP_0', '3d5ec18994fa792a6f5c6a3110fa9b7f2c739dcf']  
>
> Taproot锁定脚本: ['OP_1', '060e50b842e9bf653206284c185dc209719f0d8437071cc1bf8ae4ee0f544d59']



1）Legacy锁定脚本复杂, 交易效率低, 隐私差, 费用较高, 基于ECDSA签名；

2）SegWit锁定脚本简单, 仅包含一个空元素和公钥哈希，交易效率较高，隐私有所提升,基于ECDSA签名 ；

3）Taproot锁定脚本简单, 仅包含版本号和Taproot公钥, 交易效率高,隐藏交易复杂性，安全性最高, 基于Schnorr签名。