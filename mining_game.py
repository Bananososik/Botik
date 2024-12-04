# mining_game.py
from pyrogram import types
import json
import os
from datetime import datetime
import threading
import time

class MiningGame:
    def __init__(self):
        self.farms = {
            1: {"name": "GTX 1650", "price": 100, "rate": 10},
            2: {"name": "RTX 2060", "price": 1000, "rate": 50},
            3: {"name": "RTX 3070", "price": 5000, "rate": 100},
            4: {"name": "RTX 3080", "price": 10000, "rate": 200},
            5: {"name": "RTX 3090", "price": 20000, "rate": 400},
            6: {"name": "RTX 4060", "price": 40000, "rate": 800},
            7: {"name": "RTX 4070", "price": 80000, "rate": 1600},
            8: {"name": "RTX 4080", "price": 160000, "rate": 3200},
            9: {"name": "RTX 4090", "price": 320000, "rate": 6400},
            10: {"name": "RTX 4090 Ti", "price": 640000, "rate": 12800}
        }
        self.mining_threads = {}

    def get_user_data_path(self, user_id):
        directory = f"Users/{user_id}"
        if not os.path.exists(directory):
            os.makedirs(directory)
        return f"{directory}/data.json"

    def load_user_data(self, user_id):
        path = self.get_user_data_path(user_id)
        default_data = {"coins": 100, "farms": {}}
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if self.validate_user_data(data):
                    return data
            except Exception as e:
                print(f"Error loading user data for {user_id}: {e}")
        return default_data

    def save_user_data(self, user_id, data):
        path = self.get_user_data_path(user_id)
        try:
            # Создаем копию данных с отсортированными фермами
            save_data = {
                "coins": data.get("coins", 0),
                "farms": {}
            }
            # Сортируем и копируем данные ферм
            sorted_farm_ids = sorted(data.get("farms", {}).keys(), key=lambda x: int(x))
            for farm_id in sorted_farm_ids:
                farm_data = data["farms"][farm_id]
                save_data["farms"][farm_id] = {
                    "name": farm_data.get("name", ""),
                    "rate": farm_data.get("rate", 0),
                    "last_collection": farm_data.get("last_collection", datetime.now().timestamp())
                }
            
            # Записываем данные в файл
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"Error saving user data for {user_id}: {e}")

    def get_game_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(
            [
                ["🏪 Магазин", "💰 Баланс"],
                ["⛏ Мои фермы"],
                ["◀️ На главную"]
            ],
            resize_keyboard=True
        )
        return keyboard

    def get_shop_text(self, user_id):
        user_data = self.load_user_data(user_id)
        text = "🏪 Магазин майнинг ферм:\n\n"
        for farm_id, farm in self.farms.items():
            owned = str(farm_id) in user_data["farms"]
            status = "✅ Куплено" if owned else "❌ Не куплено"
            text += f"{'='*30}\n"
            text += f"#{farm_id}. {farm['name']}\n"
            text += f"💰 Цена: {farm['price']} монет\n"
            text += f"⚡️ Доход: {farm['rate']} монет/сек\n"
            text += f"📊 Статус: {status}\n"
            if not owned:
                text += f"🛒 Для покупки нажмите: /buy_{farm_id}\n"
            text += "\n"
        return text

    def buy_farm(self, user_id, farm_id):
        try:
            farm_id_str = str(farm_id)
            
            if farm_id not in self.farms:
                return "❌ Такой фермы не существует!"

            user_data = self.load_user_data(user_id)
            farm = self.farms[farm_id]

            if farm_id_str in user_data["farms"]:
                return "❌ У вас уже есть эта ферма!"

            if user_data["coins"] < farm["price"]:
                return f"❌ Недостаточно монет! Нужно: {farm['price']}, у вас: {user_data['coins']}"

            # Покупка фермы
            user_data["coins"] -= farm["price"]
            user_data["farms"][farm_id_str] = {
                "name": farm["name"],
                "rate": farm["rate"],
                "last_collection": datetime.now().timestamp()
            }

            # Сохраняем обновленные данные
            self.save_user_data(user_id, user_data)

            # Запускаем майнинг для новой фермы
            self.start_mining(user_id, farm_id)

            return f"✅ Вы успешно купили {farm['name']}!"

        except Exception as e:
            print(f"Ошибка при покупке фермы: {e}")
            return "❌ Произошла ошибка при покупке фермы"
            
    def get_balance(self, user_id):
        user_data = self.load_user_data(user_id)
        return f"💰 Ваш баланс: {user_data['coins']} монет"

    def get_farms_status(self, user_id):
        user_data = self.load_user_data(user_id)
        if not user_data["farms"]:
            return "У вас пока нет ферм 😢"

        text = "⛏ Ваши фермы:\n\n"
        # Сортируем ID ферм пользователя
        sorted_farm_ids = sorted(user_data["farms"].keys(), key=lambda x: int(x))
        for farm_id in sorted_farm_ids:
            farm_data = user_data["farms"][farm_id]
            text += f"🔸 {farm_data['name']}\n"
            text += f"⚡️ Производительность: {farm_data['rate']} монет/сек\n\n"
        return text

    def start_mining(self, user_id, farm_id):
        if user_id not in self.mining_threads:
            self.mining_threads[user_id] = {}
        
        if farm_id in self.mining_threads[user_id]:
            return

        def mining_process(u_id, f_id):
            while True:
                try:
                    user_data = self.load_user_data(u_id)
                    farm_id_str = str(f_id)
                    
                    if "farms" not in user_data or farm_id_str not in user_data["farms"]:
                        print(f"Farm {f_id} not found for user {u_id}")
                        break
                    
                    farm_data = user_data["farms"][farm_id_str]
                    current_time = datetime.now().timestamp()
                    last_collection = farm_data.get("last_collection", current_time)
                    rate = farm_data.get("rate", 0)
                    
                    elapsed_time = current_time - last_collection
                    coins_earned = int(elapsed_time * rate)
                    
                    if coins_earned > 0:
                        user_data["coins"] = user_data.get("coins", 0) + coins_earned
                        farm_data["last_collection"] = current_time
                        self.save_user_data(u_id, user_data)
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"Mining error for user {u_id}, farm {f_id}: {str(e)}")
                    break

        thread = threading.Thread(target=mining_process, args=(user_id, farm_id))
        thread.daemon = True
        thread.start()
        self.mining_threads[user_id][farm_id] = thread

    def validate_user_data(self, data):
        if not isinstance(data, dict):
            return False
        if "coins" not in data or not isinstance(data["coins"], (int, float)):
            return False
        if "farms" not in data or not isinstance(data["farms"], dict):
            return False
        return True