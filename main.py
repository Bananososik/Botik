from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot_token import bot_token, api_id, api_hash
from logging_utils import save_message, save_media
from mining_game import MiningGame
import os
from pyrogram import filters
import re

# Инициализация бота
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Инициализация игры
game = MiningGame()

# Словарь для хранения состояний пользователей
user_states = {}

# Главное меню
@app.on_message(filters.command("menu"))
async def menu(client, message):
    keyboard = ReplyKeyboardMarkup([
        [
            KeyboardButton("📸 Отправить фото"),
            KeyboardButton("🎯 Отправить стикер")
        ],
        [
            KeyboardButton("❓ Помощь"),
            KeyboardButton("ℹ️ Информация")
        ],
        [KeyboardButton("🔄 Сбросить")]
    ], 
    resize_keyboard=True)
    
    await message.reply(
        "Выберите действие из меню:",
        reply_markup=keyboard
    )

@app.on_message(filters.command("start"))
async def start(client, message):
    main_keyboard = ReplyKeyboardMarkup([
        ["🎮 Игры", "👤 Профиль"],
        ["📢 Информация", "⚙️ Настройки"]
    ], resize_keyboard=True)
    
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    
    # Загружаем и обновляем данные пользователя
    user_data = game.load_user_data(user_id)
    user_data["username"] = username
    game.save_user_data(user_id, user_data)
    
    await message.reply(
        "Добро пожаловать! Выберите действие из меню:",
        reply_markup=main_keyboard
    )
    save_message(username, "Бот запущен", is_bot=True)


@app.on_message(
    (filters.text & ~filters.command(["menu", "game", "shop"])) | filters.regex(r"/buy_\d+")
)
async def handle_message(client, message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    save_message(username, message.text)

    # Обработка игровых кнопок
    if message.text == "🏪 Магазин":
        await message.reply_text(game.get_shop_text(user_id))
    elif message.text == "💰 Баланс":
        await message.reply_text(game.get_balance(user_id))
    elif message.text == "⛏ Мои фермы":
        await message.reply_text(game.get_farms_status(user_id))
    elif message.text == "🏆 Топ игроков":
        await message.reply_text(game.get_top_players())
    elif message.text == "◀️ На главную":
        main_keyboard = ReplyKeyboardMarkup(
            [
                ["🎮 Игры", "👤 Профиль"],
                ["📢 Информация", "⚙️ Настройки"]
            ],
            resize_keyboard=True
        )
        await message.reply_text("Вы вернулись в главное меню", reply_markup=main_keyboard)
    elif message.text == "🎮 Игры":
        game_keyboard = game.get_game_keyboard()
        await message.reply_text("🎮 Выберите действие:", reply_markup=game_keyboard)
    elif message.text == "👤 Профиль":
        # Отображение профиля пользователя
        await message.reply_text("👤 Ваш профиль:\n\n*Имя пользователя:* {}\n*ID:* {}".format(
            message.from_user.first_name,
            message.from_user.id
        ))
    elif message.text == "📢 Информация":
        # Предоставление информации о боте
        await message.reply_text("📢 Информация:\n\nЭтот бот создан для демонстрации возможностей...")
    elif message.text == "⚙️ Настройки":
        # Предоставление настроек
        settings_keyboard = ReplyKeyboardMarkup(
            [
                ["🔔 Уведомления", "🌐 Язык"],
                ["◀️ Назад"]
            ],
            resize_keyboard=True
        )
        await message.reply_text("⚙️ Настройки:\n\nВыберите настройку, которую хотите изменить:", reply_markup=settings_keyboard)
    elif re.match(r"/buy_\d+", message.text):
        # Ваш существующий код для обработки покупки фермы
        try:
            command = message.text.strip()
            print(f"Получена команда: {command}")
            farm_id = int(command.split('_')[1])
            print(f"Попытка купить ферму ID: {farm_id} для пользователя: {user_id}")
            result = game.buy_farm(user_id, farm_id)
            await message.reply_text(result)

            # Если покупка успешна, показываем обновленный магазин
            if "успешно" in result.lower():
                await message.reply_text(game.get_shop_text(user_id))
        except (ValueError, IndexError) as e:
            print(f"Ошибка обработки команды: {e}")
            await message.reply_text("❌ Неверный формат команды!")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            await message.reply_text("❌ Произошла ошибка при покупке фермы")
    elif message.text == "◀️ Назад":
        main_keyboard = ReplyKeyboardMarkup(
            [
                ["🎮 Игры", "👤 Профиль"],
                ["📢 Информация", "⚙️ Настройки"]
            ],
            resize_keyboard=True
        )
        await message.reply_text("Вы вернулись в главное меню", reply_markup=main_keyboard)
# Обработчик фотографий
@app.on_message(filters.photo)
async def handle_photo(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        photo = message.photo
        temp_file = f"temp/{photo.file_id}.jpg"
        
        await message.download(file_name=temp_file)
        
        if os.path.exists(temp_file):
            with open(temp_file, "rb") as f:
                file_data = f.read()
                save_media(username, file_data, "photo")
            
            os.remove(temp_file)
            save_message(username, "📸 Фотография получена и сохранена")
            await message.reply("Фото успешно сохранено!")
            print(f"Фото успешно сохранено для пользователя {username}")
        
    except Exception as e:
        print(f"Ошибка при обработке фото: {str(e)}")
        print(f"Тип ошибки: {type(e)}")

# Обработчик стикеров
@app.on_message(filters.sticker)
async def handle_sticker(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or str(user_id)
        
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        file_size = message.sticker.file_size
        file_size_kb = file_size / 1024
        file_ext = ".webm" if file_size_kb > 100 else ".webp"
        
        print(f"Размер стикера: {file_size_kb:.2f} KB")
        print(f"Выбранное расширение: {file_ext}")
        
        temp_file = f"temp/{message.sticker.file_id}{file_ext}"
        
        await message.download(file_name=temp_file)
        
        if os.path.exists(temp_file):
            with open(temp_file, "rb") as f:
                file_data = f.read()
                save_media(username, file_data, "sticker", file_ext)
            
            os.remove(temp_file)
            await message.reply(f"🎯 Стикер получен и сохранен (размер: {file_size_kb:.2f} KB)")
            save_message(username, f"🎯 Стикер получен и сохранен (размер: {file_size_kb:.2f} KB)")
            print(f"Стикер успешно сохранен для пользователя {username}")
        
    except Exception as e:
        print(f"Ошибка при обработке стикера: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)

# Обработчик команды для игрового режима
@app.on_message(filters.command("game"))
async def game_menu(client, message):
    keyboard = game.get_game_keyboard()
    await message.reply_text("🎮 Добро пожаловать в игровое меню!", reply_markup=keyboard)

# Обработчик для магазина
@app.on_message(filters.command("shop"))
async def shop_command(client, message):
    args = message.text.split()
    if len(args) == 1:
        await message.reply_text(game.get_shop_text(message.from_user.id))
    elif len(args) == 2:
        try:
            farm_id = int(args[1])
            result = game.buy_farm(message.from_user.id, farm_id)
            await message.reply_text(result)
        except ValueError:
            await message.reply_text("❌ Неверный формат команды! Используйте /shop <номер фермы>")

def start_mining_processes():
    if os.path.exists("Users"):
        for user_dir in os.listdir("Users"):
            try:
                user_id = int(user_dir)
                user_data = game.load_user_data(user_id)
                for farm_id in user_data.get("farms", {}):
                    game.start_mining(user_id, int(farm_id))
            except ValueError:
                continue
            except Exception as e:
                print(f"Error starting mining for user {user_dir}: {e}")

# Запуск бота
if __name__ == "__main__":
    print("Bot started!")
    start_mining_processes()
    app.run()