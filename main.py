from pyrogram import Client, filters
from bot_token import bot_token, api_id, api_hash
from logging_utils import save_message, save_media

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_states = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    username = message.from_user.username
    user_states[username] = 'waiting_for_chromosomes'
    await message.reply("Введите количество ваших хромосом: ")
    save_message(username, "Введите количество ваших хромосом: ", is_bot=True)

@app.on_message(filters.private & ~filters.command("start"))
async def handle_message(client, message):
    username = message.from_user.username
    save_message(username, message.text)
    if user_states.get(username) == 'waiting_for_chromosomes':
        if message.text == "46":
            await message.reply("Поздравляю, вы человек!")
            save_message(username, "Поздравляю, вы человек!", is_bot=True)
        else:
            await message.reply("Вы даун!")
            save_message(username, "Вы даун!", is_bot=True)
        user_states[username] = None

@app.on_message(filters.photo)
async def handle_photo(client, message):
    username = message.from_user.username
    photo = await message.download()
    with open(photo, 'rb') as f:
        save_media(username, f.read(), 'photo')

@app.on_message(filters.sticker)
async def handle_sticker(client, message):
    username = message.from_user.username
    sticker = await message.download()
    save_media(username, sticker, 'sticker')

print("Bot started!")
app.run()