from pyrogram import Client, filters
from bot_token import bot_token, api_id, api_hash

app = Client("my_bot", api_id = api_id, api_hash = api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
def start(client, message):
    message.reply("Введите количество ваших хромосом: ")
    if message.text == "46":
        message.reply("Поздравляю, вы человек!")
    else:
        message.reply("Вы даун!")
print("Bot started!")
app.run()