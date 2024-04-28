from hades.hades import Hades
from hades.util import pip_install

pip_install(
    "git+https://github.com/dolfies/discord.py-self",
    "typing",
    "typing_extensions",
    "tls_client",
    "flask",
    "requests",
    "xxhash",
    check_exists=True
)

Hades()
