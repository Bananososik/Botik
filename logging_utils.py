# logging_utils.py
import os
from datetime import datetime

def create_user_directory(username):
    """Создает директорию для пользователя"""
    user_dir = os.path.join('Users', str(username))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def save_message(username, message, is_bot=False):
    """Сохраняет сообщение в лог"""
    try:
        user_dir = create_user_directory(username)
        log_file = os.path.join(user_dir, 'log.txt')
        timestamp = datetime.now().strftime("%d.%m.%y %H:%M:%S")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            if is_bot:
                f.write(f"{message}   {timestamp} (бот)\n\n")
            else:
                f.write(f"{message}   {timestamp} ({username})\n\n")
                
    except Exception as e:
        print(f"Ошибка при сохранении сообщения: {str(e)}")

def save_media(username, media_data, media_type):
    """Сохраняет медиафайл"""
    try:
        # Создаем директории
        user_dir = create_user_directory(username)
        media_dir = os.path.join(user_dir, 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = '.jpg' if media_type == 'photo' else '.webp'
        filename = f"{media_type}_{timestamp}{extension}"
        
        # Сохраняем файл
        file_path = os.path.join(media_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(media_data)
        
        print(f"Медиафайл сохранен: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"Ошибка при сохранении медиафайла: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        raise