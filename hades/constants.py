from typing import Dict, List, Any, TypedDict

from discord import HypeSquadHouse
import requests
import re

HYPESQUAD: Dict[str, Any] = {
    "balance": HypeSquadHouse.balance,
    "bravery": HypeSquadHouse.bravery,
    "brilliance": HypeSquadHouse.brilliance
}

HEADERS: Dict[str, str] = {
    "X-Requested-With": "XMLHttpRequest",
}

NITRO_REGEX: re.Pattern = re.compile(r"(discord.com/gifts/|discordapp.com/gifts/|discord.gift/)([a-zA-Z0-9]+)")
PRIVNOTE_REGEX: re.Pattern = re.compile(r"https://privnote\.com/[a-zA-Z0-9]+#[a-zA-Z0-9]+")
PACKS: List[str] = list(set(
    requests.get("https://raw.githubusercontent.com/nullsx/PACK-BIBLE-S2/main/Another_BKC_Pack_Bible.txt").text.strip().split("\n\n") +
    requests.get("https://raw.githubusercontent.com/nullsx/PACK-BIBLE-S2/main/Huge_Pack_Bible.txt").text.strip().split("\n\n")
))
