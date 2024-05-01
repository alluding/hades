"""
A quick util package for Hades.
"""
from __future__ import annotations
from typing import Dict, Optional, Union

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from tls_client import Session as _Session
from curl_cffi.requests import Session
from bs4 import BeautifulSoup

from .constants import HEADERS, PLATFORM, UserInfo

import subprocess

session: _Session = _Session(
    client_identifier="chrome_119",
    random_tls_extension_order=True
)

session: Session = Session(
    impersonate="chrome119",
    headers={
        "User-Agent": "Mozilla/5.0 (Linux i582 x86_64) AppleWebKit/535.47 (KHTML, like Gecko) Chrome/119.0.1621.282 Safari/537",
        "X-Requested-With": "XMLHttpRequest"
    },
    cookies={
        "User": "Anonymous",
        "ping": "true"
    }
)

class PrivnoteDec:
    """
    A simple class used for decrypting data from Privnote.

    - The algorithm used for encryption in Privnote is fairly simple and was easy to reverse.
    """
    PASS_CHARS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"

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
    A function for reading and destroying privnotes, utilizing `tls_client` to bypass Cloudflare.
    """
    response = session.delete(url, headers=HEADERS)
    password = parse_password(url)
    
    data, decryptor = response.json().get("data", "Failed to get note data."), PrivnoteDec()

    return decryptor.decrypt(
        ciphertext=data, 
        password=password
    ) if password else "No password found"

def parse_data(data: str) -> Union[bool, str, UserInfo]:
    soup = BeautifulSoup(data, "html.parser")

    if "You can only resolve" in data:
        return "Rate limited for 30 minutes."

    if "Seems like that user was not found" in data:
        return f"That user wasn't found!"

    if "Here's the information we found" in data:
        rows = soup.find_all('tr')
        user_info: UserInfo = {row.find('th').text.strip(): row.find('td').text.strip() for row in rows}
        return user_info

def resolve_user(
    username: str,
    platform: Literal["ps", "xbl"]
) -> Union[bool, str, UserInfo]:
    response = requests.post(
        "https://xresolver.com/ajax/tool.php",
        data={PLATFORM.get(platform, "psnUsername"): username}
    )
    return parse_data(response.text)
        
# def check_package_exists(package_name: str) -> str:
#     installed_packages = subprocess.check_output(["pip", "list"]).decode("utf-8")
#     return "installed" if package_name.lower() in installed_packages.lower() else "not installed"

# def pip_install(*packages: str, check_exists: bool = False) -> None:
#     package_statuses = {package: check_package_exists(package) for package in packages}

#     for package, status in package_statuses.items():
#         if check_exists and status == "installed":
#             print(f"{package} is already installed.")
#         else:
#             subprocess.run(["pip", "install", package])
#             print(f"{package} has been successfully installed.")
