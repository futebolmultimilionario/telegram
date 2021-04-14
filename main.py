from telethon import TelegramClient, events
from settings import config
import asyncio
import logging

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)

client = TelegramClient("listener", config.API_ID, config.API_HASH)
client.parse_mode = "md"


async def get_latest_id(group_id):
    latest_id = None
    async for m in client.iter_messages(group_id):
        latest_id = m.id
        break
    return latest_id


@client.on(events.NewMessage())
async def forward(event):
    message = event.message
    if event.chat_id in config.IO:

        for n in range(len(config.IO[event.chat_id])):
            await client.send_message(
                config.IO[event.chat_id][n], message=event.text, file=message.media
            )


def main():
    client.start()
    print("Userbot on!")
    client.run_until_disconnected()


if __name__ == "__main__":
    #asyncio.run(sync()) #remove the "#" at the start
    # of the line if you added new ids, run the script once,
    # then put it back.
    main()
