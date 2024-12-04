# main.py
from pyrogram import Client, filters
from bot_token import bot_token, api_id, api_hash
from logging_utils import save_message, save_media
import os

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_states = {}

@app.on_message(filters.photo)
async def handle_photo(client, message):
    try:
        username = message.from_user.username
        if not os.path.exists("temp"):
            os.makedirs("temp")
            
        file_path = f"temp/{message.photo.file_unique_id}.jpg"
        
        await message.download(file_name=file_path)
        
        with open(file_path, "rb") as photo_file:
            photo_data = photo_file.read()
            save_media(username, photo_data, "photo")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        save_message(username, "📸 Фотография получена и сохранена")
        
    except Exception as e:
        print(f"Ошибка при обработке фото: {str(e)}")

@app.on_message(filters.sticker)
async def handle_sticker(client, message):
    try:
        username = message.from_user.username
        if not os.path.exists("temp"):
            os.makedirs("temp")
            
        file_path = f"temp/{message.sticker.file_unique_id}.webp"
        
        await message.download(file_name=file_path)
        
        with open(file_path, "rb") as sticker_file:
            sticker_data = sticker_file.read()
            save_media(username, sticker_data, "sticker")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        save_message(username, "🎯 Стикер получен и сохранен")
        
    except Exception as e:
        print(f"Ошибка при обработке стикера: {str(e)}")

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

        
print("Bot started!")
app.run()