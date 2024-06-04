import re
import asyncio
import datetime

from telethon import TelegramClient, events, sessions
from telethon.tl import functions, types

from .constants import STICKER_PACK_IDS, TELETHON_ACCESS_HASH, TELETHON_API_HASH, TELETHON_API_ID, TELETHON_SESSION_STRING
from .cloudflare import insert_total_pack_usage

# Create a TelegramClient instance
client = TelegramClient(sessions.StringSession(TELETHON_SESSION_STRING), TELETHON_API_ID, TELETHON_API_HASH)

current_pack_index = None

#================#
# Event Handlers #
#================#

# PackStatsHandler is called in response to a /packstats command
@client.on(events.NewMessage(chats="@Stickers", incoming=True, pattern=r"Stats for the sticker set((?!for).)*:"))
async def pack_stats_handler(event: events.NewMessage.Event):
    # Gather stats and insert them into the database
    total_usage = int(re.search(r"Total usage: \d*", event.message.message).group().split(":")[1].strip())
    total_installed = int(re.search(r"Total installed: \d*", event.message.message).group().split(":")[1].strip())
    total_removed = int(re.search(r"Total removed: \d*", event.message.message).group().split(":")[1].strip())

    insert_total_pack_usage(str(STICKER_PACK_IDS[current_pack_index]), event.date.strftime("%Y-%m-%d %H:%M:%S"), total_usage, total_installed, total_removed)

    await get_stats_from_next_pack()

#=========================#
# on_start and event loop #
#=========================#

# Send message to @Stickers to get stats for the next pack
async def get_stats_from_next_pack():
    global current_pack_index

    if current_pack_index is None:
        current_pack_index = 0
    else:
        current_pack_index += 1

    if current_pack_index >= len(STICKER_PACK_IDS):
        current_pack_index = 0

    current_pack_id = STICKER_PACK_IDS[current_pack_index]
    sticker_pack: types.StickerPack = await client(functions.messages.GetStickerSetRequest(types.InputStickerSetID(id=int(current_pack_id), access_hash=int(TELETHON_ACCESS_HASH)), 0))

    await client.send_message("@Stickers", "/packstats", schedule=datetime.timedelta(seconds=30))
    await client.send_message("@Stickers", sticker_pack.set.short_name, schedule=datetime.timedelta(seconds=30))

async def main():
    await client.start()
    await get_stats_from_next_pack()
    await client.run_until_disconnected()

def run_event_loop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
