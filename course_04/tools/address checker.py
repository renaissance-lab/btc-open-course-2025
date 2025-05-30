from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script

setup('testnet')

alice_priv = PrivateKey("cRxebG1hY6vVgS9CSLNaEbEJaXkpZvc6nFeqqGT7v6gcW7MbzKNT")
alice_pub = alice_priv.get_public_key()

import hashlib
hash1 = hashlib.sha256(b"helloworld").hexdigest()
hash2 = hashlib.sha256(b"helloaaron").hexdigest()

script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])
script2 = Script(['OP_SHA256', hash2, 'OP_EQUALVERIFY', 'OP_TRUE'])

bob_priv = PrivateKey("cSNdLFDf3wjx1rswNL2jKykbVkC6o56o5nYZi4FUkWKjFn2Q5DSG")
bob_pub = bob_priv.get_public_key()
bob_script = Script([bob_pub.to_x_only_hex(), 'OP_CHECKSIG'])

# 树顺序1
tree1 = [[script1, script2], bob_script]
addr1 = alice_pub.get_taproot_address(tree1)
print("顺序1地址：", addr1.to_string())

# 树顺序2
tree2 = [script1, [script2, bob_script]]
addr2 = alice_pub.get_taproot_address(tree2)
print("顺序2地址：", addr2.to_string())