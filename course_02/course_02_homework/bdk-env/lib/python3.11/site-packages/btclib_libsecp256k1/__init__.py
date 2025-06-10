# Copyright (C) The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

"""Pure python cffi bindings to libsecp256k1: https://github.com/bitcoin-core/secp256k1."""

import pathlib

import _btclib_libsecp256k1  # type: ignore

ffi = _btclib_libsecp256k1.ffi
if "lib" in dir(_btclib_libsecp256k1):
    lib = _btclib_libsecp256k1.lib
else:
    path = pathlib.Path(_btclib_libsecp256k1.__file__).parent
    suffixes = [".dll", ".so", ".dylib"]
    for suffix in suffixes:
        for file in path.glob(f"libsecp256k1*{suffix}*"):
            try:
                lib = ffi.dlopen(str(file))
                break
            except OSError:
                pass
