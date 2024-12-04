# main.py
from pyrogram import Client, filters
from bot_token import bot_token, api_id, api_hash
from logging_utils import save_message, save_media
import os

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_states = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    user_states[user_id] = 'waiting_for_chromosomes'
    await message.reply("Введите количество ваших хромосом: ")
    save_message(username, "Введите количество ваших хромосом: ", is_bot=True)

@app.on_message(filters.text & ~filters.command("start"))
async def handle_message(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    save_message(username, message.text)
    if user_states.get(user_id) == 'waiting_for_chromosomes':
        if message.text == "46":
            await message.reply("Поздравляю, вы человек!")
            save_message(username, "Поздравляю, вы человек!", is_bot=True)
        else:
            await message.reply("Вы даун!")
            save_message(username, "Вы даун!", is_bot=True)
        user_states[user_id] = None

@app.on_message(filters.photo)
async def handle_photo(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        # Changed this part - directly use message.photo
        photo = message.photo
        temp_file = f"temp/{photo.file_id}.jpg"
        
        # Download using file_id
        await message.download(file_name=temp_file)
        
        if os.path.exists(temp_file):
            with open(temp_file, "rb") as f:
                file_data = f.read()
                save_media(username, file_data, "photo")
            
            os.remove(temp_file)
            save_message(username, "📸 Фотография получена и сохранена")
            print(f"Фото успешно сохранено для пользователя {username}")
        
    except Exception as e:
        print(f"Ошибка при обработке фото: {str(e)}")
        print(f"Тип ошибки: {type(e)}")

@app.on_message(filters.sticker)
async def handle_sticker(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        # Получаем размер файла напрямую из сообщения (в байтах)
        file_size = message.sticker.file_size
        file_size_kb = file_size / 1024
        
        # Определяем расширение на основе размера в килобайтах
        file_ext = ".webm" if file_size_kb > 100 else ".webp"
        
        print(f"Размер стикера: {file_size_kb:.2f} KB")
        print(f"Выбранное расширение: {file_ext}")
        
        temp_file = f"temp/{message.sticker.file_id}{file_ext}"
        
        # Скачиваем стикер
        await message.download(file_name=temp_file)
        
        if os.path.exists(temp_file):
            with open(temp_file, "rb") as f:
                file_data = f.read()
                # Передаем расширение в функцию save_media
                save_media(username, file_data, "sticker", file_ext)
            
            os.remove(temp_file)
            save_message(username, f"🎯 Стикер получен и сохранен (размер: {file_size_kb:.2f} KB)")
            print(f"Стикер успешно сохранен для пользователя {username}")
        
    except Exception as e:
        print(f"Ошибка при обработке стикера: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)

print("Bot started!")
app.run()