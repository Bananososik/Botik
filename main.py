# main.py
from pyrogram import Client, filters
from bot_token import bot_token, api_id, api_hash
from logging_utils import save_message, save_media
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_states = {}

@app.on_message(filters.command("menu"))
async def menu(client, message):
    keyboard = ReplyKeyboardMarkup([
        # Первый ряд
        [
            KeyboardButton("📸 Отправить фото"),
            KeyboardButton("🎯 Отправить стикер")
        ],
        # Второй ряд
        [
            KeyboardButton("❓ Помощь"),
            KeyboardButton("ℹ️ Информация")
        ],
        # Третий ряд
        [KeyboardButton("🔄 Сбросить")]
    ], 
    resize_keyboard=True,
    one_time_keyboard=False)
    
    await message.reply(
        "Выберите действие из меню:",
        reply_markup=keyboard
    )

# Исправленный обработчик для кнопок меню
@app.on_message(filters.text & ~filters.command(["start", "menu"]))  # указываем список команд для исключения
async def handle_menu_buttons(client, message):
    if message.text == "📸 Отправить фото":
        await message.reply("Отправьте фотографию")
    
    elif message.text == "🎯 Отправить стикер":
        await message.reply("Отправьте стикер")
    
    elif message.text == "❓ Помощь":
        await message.reply("Здесь будет текст помощи")
    
    elif message.text == "ℹ️ Информация":
        await message.reply("Здесь будет информация о боте")
    
    elif message.text == "🔄 Сбросить":
        await message.reply("Сброс выполнен")

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

from pyrogram import Client, filters
from mining_game import MiningGame

# Инициализация игры
game = MiningGame()

# Обработчик команды для перехода в игровой режим
@app.on_message(filters.command("game"))
async def game_menu(client, message):
    keyboard = game.get_game_keyboard()
    await message.reply_text("🎮 Добро пожаловать в игровое меню!", reply_markup=keyboard)

# Обработчик для покупки ферм
@app.on_message(filters.command("shop"))
async def shop_command(client, message):
    args = message.text.split()
    if len(args) == 1:
        # Показываем список доступных ферм
        await message.reply_text(game.get_shop_text(message.from_user.id))
    elif len(args) == 2:
        try:
            farm_id = int(args[1])
            result = game.buy_farm(message.from_user.id, farm_id)
            await message.reply_text(result)
        except ValueError:
            await message.reply_text("❌ Неверный формат команды! Используйте /shop <номер фермы>")

# Обработчик текстовых сообщений для кнопок
@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if message.text == "🏪 Магазин":
        await message.reply_text(game.get_shop_text(message.from_user.id))
    elif message.text == "💰 Баланс":
        await message.reply_text(game.get_balance(message.from_user.id))
    elif message.text == "⛏ Мои фермы":
        await message.reply_text(game.get_farms_status(message.from_user.id))
    # Продолжение предыдущего кода...
    elif message.text == "◀️ На главную":
        # Создаем основную клавиатуру
        main_keyboard = types.ReplyKeyboardMarkup(
            [
                ["🎮 Игры", "👤 Профиль"],  # Первый ряд кнопок
                ["📢 Информация", "⚙️ Настройки"],  # Второй ряд кнопок
            ],
            resize_keyboard=True
        )
        await message.reply_text("Вы вернулись в главное меню", reply_markup=main_keyboard)

# Добавим обработчик для кнопки перехода в игры
@app.on_message(filters.regex("^🎮 Игры$"))
async def games_menu(client, message):
    game_keyboard = game.get_game_keyboard()
    await message.reply_text("🎮 Выберите действие:", reply_markup=game_keyboard)

# Добавим обработчик для запуска всех майнинг процессов при старте бота
@app.on_start()
async def start_mining_processes():
    # Проходим по всем файлам в директории Users
    if os.path.exists("Users"):
        for user_dir in os.listdir("Users"):
            try:
                user_id = int(user_dir)
                user_data = game.load_user_data(user_id)
                # Запускаем майнинг для каждой фермы пользователя
                for farm_id in user_data.get("farms", {}):
                    game.start_mining(user_id, int(farm_id))
            except ValueError:
                continue
            except Exception as e:
                print(f"Error starting mining for user {user_dir}: {e}")    

print("Bot started!")
app.run()