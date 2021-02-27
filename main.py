from telethon import TelegramClient, events
from settings import config
import asyncio
import aiosqlite
from aiosqlite import OperationalError
import logging

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)

client = TelegramClient("listener", config.API_ID, config.API_HASH)
client.parse_mode = "md"


async def add_group(group_id):
    async with aiosqlite.connect("replies.db") as db:
        stat = f"""CREATE TABLE '{group_id}' 
        ('input_id' INTEGER NOT NULL, 
        'output_id' INTEGER NOT NULL,
        PRIMARY KEY('input_id'));"""
        await db.execute(stat)
        await db.commit()


async def add_message(group_id, input_id, output_id):
    async with aiosqlite.connect("replies.db") as db:
        stat = f"""INSERT INTO '{group_id}' VALUES ({input_id}, {output_id})"""
        print(
            f"""I sent a message in {group_id} which ID is {output_id}. The original ID is: {input_id}"""
        )
        await db.execute(stat)
        await db.commit()


async def retrieve_info(group_id, input_id):
    async with aiosqlite.connect("replies.db") as db:
        stat = f"""SELECT * FROM '{group_id}' WHERE input_id = {input_id}"""
        cur = await db.execute(stat)
        res = await cur.fetchall()
        print(
            f"Replying to id: {res[0][1]} which is linked to the original id: {res[0][0]}"
        )
        return res[0][1]


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

        if event.message.is_reply:
            for n in range(len(config.IO[event.chat_id])):
                await client.send_message(
                    config.IO[event.chat_id][n],
                    message=event.text,
                    file=message.media,
                    reply_to=await retrieve_info(
                        config.IO[event.chat_id][n], message.reply_to.reply_to_msg_id
                    ),
                )
                await add_message(
                    config.IO[event.chat_id][n],
                    message.id,
                    await get_latest_id(config.IO[event.chat_id][n]),
                )

        else:
            for n in range(len(config.IO[event.chat_id])):
                await client.send_message(
                    config.IO[event.chat_id][n], message=event.text, file=message.media
                )
                await add_message(
                    config.IO[event.chat_id][n],
                    message.id,
                    await get_latest_id(config.IO[event.chat_id][n]),
                )


def main():
    client.start()
    print("Userbot on!")
    client.run_until_disconnected()


async def sync():
    for key, value in config.IO.items():
        for n in range(len(value)):
            try:
                await add_group(value[n])
            except OperationalError as e:
                print(f"\n{key} already in the Database.\n{e}\n")
                pass


if __name__ == "__main__":
    #asyncio.run(sync()) #remove the "#" at the start
    # of the line if you added new ids, run the script once,
    # then put it back.
    main()
