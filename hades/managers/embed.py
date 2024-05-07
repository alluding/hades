from aiohttp import ClientSession
from discord import Embed
from urllib.parse import quote, urlencode
import typing


def rgb_to_hex(rgb: typing.Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


async def get_embed(
    embed: Embed,
    provider: typing.Optional[str] = None,
    provider_url: typing.Optional[str] = None,
    video: typing.Optional[str] = None
) -> str:
    if embed.fields:
        return  # Fields currently unsupported.

    params: typing.Dict[str, str] = {
        "provider": provider if provider else "",
        "author": embed.author.name if embed.author and embed.author.name else "",
        "title": embed.title if embed.title else "",
        "color": rgb_to_hex(embed.colour.to_rgb()) if embed.colour else "",
        "media_type": "none" if not embed.thumbnail else "thumbnail",
        "desc": embed.description if embed.description else ""
    }
    if video:
        params["media_type"] = "video"

    url: str = f"https://embedl.ink/?deg=&providerurl=&{urlencode(params)}"

    async with ClientSession() as session:
        data: typing.Dict[str, typing.Any] = {
            "url": url.replace("https://embedl.ink/", ""),
            "providerName": provider if provider else "",
            "providerUrl": provider_url if provider_url else "",
            "authorName": embed.author.name if embed.author and embed.author.name else "",
            "authorUrl": embed.url if embed.url else "",
            "title": embed.title if embed.title else "",
            "mediaType": params["media_type"],
            "mediaUrl": embed.thumbnail.url if embed.thumbnail and embed.thumbnail.url else "",
            "mediaThumb": None,
            "description": embed.description if embed.description else ""
        }
        async with session.post(
            "https://embedl.ink/api/create",
            data=data
        ) as result:
            data: typing.Dict[str, typing.Any] = await result.json()
            code = data.get("code") if data.get("success") else "Failed to get code."

    return f"https://embedl.ink/e/{code}"


def hidden(value: str) -> str:
    return (
        "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"
        f" _ _ _ _ _ _ {value}"
    )
