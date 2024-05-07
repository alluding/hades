# Hades
### An advanced multi-purpose Discord self-bot, currently a work in progress.
#### FYI: I'm tempted to just archive this. I have NO ideas for commands, so unless people start suggesting commands, this is probably never going to be finished. :sob:

# Features
- Custom API/wrapper for embeds (since Discord removed embeds for users ages ago).
- Customizable features such as prefixes, etc. (with or without embeds).

# Custom API/wrapper
~~I created a mini functional API for creating embeds just in case people want to spice things up a bit. Anyway, since it's based on an API, the embeds are limited; they can't have markdown like Discord bots can. I wish they could, but sadly, they can't. So they're going to be a bit plain. Besides that, image, thumbnail image, color, title, and description are supported. I know footer is possible; I just don't feel like messing with the template for the API as of now. To start the API, just open a separate terminal and run `python3 hades/api/start.py`. **Possibly**, you might need to tamper with `hades/managers/embed.py` and change the `base_url` depending on the situation. That is just what worked for **ME**.~~

This is now not required, I have found a fast reliable external API that allows embedding for EVERYONE, even those who don't have web-servers. But, I will leave the original API in it, just in case someone wants to play around and have embedding with a custom web-server domain.
