"""
A quick util package for Hades.
"""
from __future__ import annotations
from typing import Dict, Optional, Union, Literal, ClassVar

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from curl_cffi.requests import Session
from bs4 import BeautifulSoup

from .constants import HEADERS

import subprocess

session: Session = Session(
    impersonate="chrome119",
    headers={
        "User-Agent": "Mozilla/5.0 (Linux i582 x86_64) AppleWebKit/535.47 (KHTML, like Gecko) Chrome/119.0.1621.282 Safari/537",
        "X-Requested-With": "XMLHttpRequest"
    },
    cookies={}
)


class PrivnoteDec:
    """
    A simple class used for decrypting data from Privnote.

    - The algorithm used for encryption in Privnote is fairly simple and was easy to reverse.
    """
    PASS_CHARS: ClassVar[str] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"

    def __init__(self) -> None:
        pass

    def SSLKey(
        self,
        pw_bytes: bytearray,
        salt: bytearray
    ) -> Dict[str, Union[bytearray, bytearray]]:
        pw = pw_bytes + salt
        res = hashlib.md5(pw).digest()

        temp_hash = res
        for _ in range(2):
            temp_hash = hashlib.md5(temp_hash + pw).digest()
            res += temp_hash

        return {
            "key": res[:4*8],
            "iv": res[4*8:4*8+16]
        }

    def decrypt(
        self,
        ciphertext: bytes,
        password: bytearray
    ) -> str:
        decoded_cipher = base64.b64decode(ciphertext)
        salt = decoded_cipher[8:16]

        gen_ssl = self.SSLKey(password, salt)
        key, iv = gen_ssl["key"], gen_ssl["iv"]
        cipher = AES.new(key, AES.MODE_CBC, iv, use_aesni=True)

        decrypted_bytes = unpad(
            cipher.decrypt(decoded_cipher[16:]),
            cipher.block_size
        )
        return decrypted_bytes.decode()


def parse_password(value: str) -> Optional[bytearray]:
    if "privnote.com/" in value:
        value = value.split(r"https://privnote.com/")[1]
        _id, password_str = value.split("#", maxsplit=1)
        return bytearray(password_str, encoding="utf-8") if password_str else None


def read_note(url: str) -> str:
    """
    A function for reading and destroying privnotes, utilizing `curl_cffi` to bypass Cloudflare.
    """
    response = session.delete(url, headers=HEADERS)
    password = parse_password(url)

    data, decryptor = response.json().get(
        "data",
        "Failed to get note data."
    ), PrivnoteDec()

    return decryptor.decrypt(
        ciphertext=data,
        password=password
    ) if password else "No password found"
