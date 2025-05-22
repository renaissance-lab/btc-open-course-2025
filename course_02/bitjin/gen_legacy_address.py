from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey

# Set network to testnet
setup('testnet')

# Generate a new random private key
priv = PrivateKey()  # random by default
wif = priv.to_wif()  # testnet WIF
pub = priv.get_public_key()
addr = pub.get_segwit_address()  # P2WPKH (bc1...)

print("Private key (WIF):", wif)
print("Public key:", pub.to_hex())
print("P2WPKH SegWit Address:", addr.to_string())

#get testnet faucet
#source https://bitcoinfaucet.uo1.net/send.php

#ex
#Private key (WIF): cStwaM5VbuyfByVFZW82y9frazx5Pe3dxma6mR4yctsHD8ezBtq1
#Public key: 0351ac29a46edcf40bad55a5bb3770caf317205e2aa193198da14a794d5afefdad
# P2WPKH SegWit Address: tb1q97taqahnh4akf69jazqu57p5h7gypfmm5ktare