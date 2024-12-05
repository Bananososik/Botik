# logging_utils.py
import os
from datetime import datetime

def create_user_directory(user_id, username=None):
    """Создает директорию для пользователя"""
    user_dir = os.path.join('Users', str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        # Создаем файл username.txt при создании новой папки пользователя
        if username:
            username_path = os.path.join(user_dir, 'username.txt')
            with open(username_path, 'w', encoding='utf-8') as f:
                f.write(username)
    return user_dir

def save_message(user_id, username, message, is_bot=False):
    """Сохраняет сообщение в лог"""
    try:
        user_dir = create_user_directory(user_id, username)
        log_file = os.path.join(user_dir, 'log.txt')
        timestamp = datetime.now().strftime("%d.%m.%y %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            if is_bot:
                f.write(f"{message}   {timestamp} (бот)\n\n")
            else:
                f.write(f"{message}   {timestamp} ({username})\n\n")
    except Exception as e:
        print(f"Ошибка при сохранении сообщения: {str(e)}")

def save_media(user_id, username, media_data, media_type, file_ext=None):
    """Сохраняет медиафайл"""
    try:
        user_dir = create_user_directory(user_id, username)
        media_dir = os.path.join(user_dir, 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = file_ext if file_ext else ('.jpg' if media_type == 'photo' else '.webp')
        filename = f"{media_type}_{timestamp}{extension}"

        file_path = os.path.join(media_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(media_data)

        print(f"Медиафайл сохранен: {file_path}")
        return file_path

    except Exception as e:
        print(f"Ошибка при сохранении медиафайла: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        raise