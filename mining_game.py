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
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {"coins": 100, "farms": {}}

    def save_user_data(self, user_id, data):
        path = self.get_user_data_path(user_id)
        with open(path, 'w') as f:
            json.dump(data, f)

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
            status = "✅" if owned else "❌"
            text += f"{farm_id}. {farm['name']} - {farm['price']}💰\n"
            text += f"⚡️ Производительность: {farm['rate']} монет/сек\n"
            text += f"Статус: {status}\n\n"
        text += "\nДля покупки используйте команду /shop <номер фермы>"
        return text

    def buy_farm(self, user_id, farm_id):
        if str(farm_id) not in self.farms:
            return "❌ Неверный номер фермы!"

        user_data = self.load_user_data(user_id)
        farm = self.farms[farm_id]

        if str(farm_id) in user_data["farms"]:
            return "❌ У вас уже есть эта ферма!"

        if user_data["coins"] < farm["price"]:
            return "❌ Недостаточно монет!"

        user_data["coins"] -= farm["price"]
        user_data["farms"][str(farm_id)] = {
            "name": farm["name"],
            "rate": farm["rate"],
            "last_collection": datetime.now().timestamp()
        }
        self.save_user_data(user_id, user_data)
        self.start_mining(user_id, farm_id)
        
        return f"✅ Вы успешно купили {farm['name']}!"

    def get_balance(self, user_id):
        user_data = self.load_user_data(user_id)
        return f"💰 Ваш баланс: {user_data['coins']} монет"

    def get_farms_status(self, user_id):
        user_data = self.load_user_data(user_id)
        if not user_data["farms"]:
            return "У вас пока нет ферм 😢"

        text = "⛏ Ваши фермы:\n\n"
        for farm_id, farm_data in user_data["farms"].items():
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
                    farm_data = user_data["farms"][str(f_id)]
                    current_time = datetime.now().timestamp()
                    elapsed_time = current_time - farm_data["last_collection"]
                    
                    coins_earned = int(elapsed_time * farm_data["rate"])
                    if coins_earned > 0:
                        user_data["coins"] += coins_earned
                        farm_data["last_collection"] = current_time
                        self.save_user_data(u_id, user_data)
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"Mining error for user {u_id}, farm {f_id}: {e}")
                    break

        thread = threading.Thread(target=mining_process, args=(user_id, farm_id))
        thread.daemon = True
        thread.start()
        self.mining_threads[user_id][farm_id] = thread