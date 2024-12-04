import os
from datetime import datetime

def create_user_directory(username):
    user_dir = os.path.join('Users', username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def save_message(username, message, is_bot=False):
    user_dir = create_user_directory(username)
    log_file = os.path.join(user_dir, 'log.txt')
    timestamp = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    with open(log_file, 'a', encoding='utf-8') as f:
        if is_bot:
            f.write(f"{message}   {timestamp} (бот)\n\n")
        else:
            f.write(f"{message}   {timestamp} ({username})\n\n")

def save_media(username, media, media_type):
    user_dir = create_user_directory(username)
    timestamp = datetime.now().strftime("%d.%m.%y %H-%M-%S")
    media_dir = os.path.join(user_dir, timestamp)
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    count = 1
    media_path = os.path.join(media_dir, f"{media_type}")
    while os.path.exists(media_path):
        media_path = os.path.join(media_dir, f"{media_type} ({count})")
        count += 1
    
    with open(media_path, 'wb') as f:
        f.write(media)  # Assuming media is in bytes