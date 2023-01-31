"""
The MIT License (MIT)

Copyright (c) 2023-present MrSniFo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# ------ Discord ------
from discord import Embed

# ------ Crypto ------
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from binascii import Error


def encrypt(key: str, source: str, encode=True) -> str:
    key = SHA256.new(bytes(key, 'utf-8')).digest()  # use SHA-256 over our key to get a proper-sized AES key
    iv = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    source = bytes(source, 'utf-8')
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = iv + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key: str, source: str, decode=True) -> bool | str:
    try:
        if decode:
            source = base64.b64decode(source.encode("latin-1"))
        key = SHA256.new(bytes(key, 'utf-8')).digest()  # use SHA-256 over our key to get a proper-sized AES key
        iv = source[:AES.block_size]  # extract the IV from the beginning
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        data = decryptor.decrypt(source[AES.block_size:])  # decrypt
        padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
        if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
            return False
        return data[:-padding].decode("utf-8")
    except (ValueError, Error):
        return False


def embed_wrong(msg: str) -> Embed:
    """
    This function will generate embed message.

    :return:`discord.Embed`
    """
    embed = Embed(description=f"**It seems something wrong** :speak_no_evil:\n{msg}", colour=0x36393f)
    return embed
