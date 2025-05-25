# Copyright (C) The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

"""
Variant of Elliptic Curve Schnorr Signature Algorithm (ECSSA), according.

to BIP340-Schnorr: https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki
"""
from __future__ import annotations

import secrets

from . import ffi, lib

ctx = lib.secp256k1_context_create(769)


def sign(
    msg_bytes: bytes, prvkey: bytes | int, aux_rand32: bytes | None = None
) -> bytes:
    """Create a Schnorr signature."""

    if isinstance(prvkey, int):
        prvkey_bytes = prvkey.to_bytes(32, "big")
    else:
        prvkey_bytes = prvkey

    keypair = ffi.new("secp256k1_keypair *")
    lib.secp256k1_keypair_create(ctx, keypair, prvkey_bytes)

    sig = ffi.new("char[64]")

    if not aux_rand32:
        aux_rand32 = secrets.token_bytes(32)
    aux_rand32 = b"\x00" * (32 - len(aux_rand32)) + aux_rand32
    if lib.secp256k1_schnorrsig_sign(ctx, sig, msg_bytes, keypair, aux_rand32):
        return ffi.unpack(sig, 64)
    raise RuntimeError


def verify(msg_bytes: bytes, pubkey_bytes: bytes, signature_bytes: bytes) -> int:
    """Verify a Schhnorr signature."""

    if len(pubkey_bytes) == 32:
        pubkey_bytes = b"\x02" + pubkey_bytes

    pubkey = ffi.new("secp256k1_pubkey *")
    lib.secp256k1_ec_pubkey_parse(ctx, pubkey, pubkey_bytes, len(pubkey_bytes))

    xonly_pubkey = ffi.new("secp256k1_xonly_pubkey *")
    lib.secp256k1_xonly_pubkey_from_pubkey(ctx, xonly_pubkey, ffi.new("int *"), pubkey)

    return lib.secp256k1_schnorrsig_verify(
        ctx, signature_bytes, msg_bytes, len(msg_bytes), xonly_pubkey
    )
