import datetime
import glob
import json
import logging
import os
import shutil
import subprocess

import dotenv
import requests

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

config = dotenv.dotenv_values('.env')
SSH_HOST = config['SSH_HOST']
SSH_USER = config['SSH_USER']
SSH_PORT = config['SSH_PORT']
SSH_PRIVATE_KEY_PATH = config['SSH_PRIVATE_KEY_PATH']
TG_BOT_TOKEN = config['TG_BOT_TOKEN']
TG_CHAT_ID = config['TG_CHAT_ID']

with open('backup_folders.json') as f:
    settings = json.load(f)


def send_telegram_message(msg: str):
    logging.info(f'[Send message] {msg}')
    r = requests.post(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
                      f'?parse_mode=HTML&chat_id={TG_CHAT_ID}&text={msg}', timeout=10)
    if r.status_code != 200:
        logging.error(f'[Telegram error] {r.status_code}, {r.text}')


def catch_errors(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as err:
            logging.error(err)
            send_telegram_message(f'❌🔄 Backup failed: {err}')
    return wrapper


def execute(command):
    logging.info('[Run command] ' + str(command))
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = process.wait()
    out, err = process.communicate()
    if exit_code != 0:
        raise subprocess.CalledProcessError(returncode=process.returncode, cmd=str(err))
    return out


def size_to_human(num: int) -> str:
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}B"
        num /= 1024.0
    return f"{num:.1f} YB"


def human_to_size(human: str) -> int:
    human = human.strip().upper().replace(' ', '')
    units = {'': 0, "B": 0, "K": 1, "M": 2, "G": 3, "T": 4, "P": 5, "E": 6, "Z": 7, "Y": 8}
    number_part, unit_part = '', ''

    for char in human:
        if char.isdigit() or char == '.' or char == ',':
            number_part += char
        elif char.isalpha() and char in units:
            unit_part += char

    number = float(number_part.replace(',', '.'))
    unit = unit_part.rstrip('B')
    return int(number * (1024 ** units[unit]))


@catch_errors
def make_backup(archive):
    send_telegram_message(f'▶️🔄 Starting backup: {archive["name"]}')

    stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    name = f'{archive["name"]}_{stamp}'
    temp_folder = os.path.join('temp', name)

    shutil.rmtree('temp', ignore_errors=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs(settings['backup_folder_name'], exist_ok=True)
    os.makedirs(temp_folder)

    for remote_dir in archive["remote_folders"]:
        cmd = f'scp -r -P {SSH_PORT} -i {SSH_PRIVATE_KEY_PATH} {SSH_USER}@{SSH_HOST}:{remote_dir} {temp_folder}'
        execute(cmd)

    archive_name = os.path.join(settings['backup_folder_name'], f'{archive["name"]}_{stamp}')
    shutil.make_archive(archive_name, 'zip', temp_folder)
    shutil.rmtree('temp', ignore_errors=True)

    backup_size = os.path.getsize(f"{archive_name}.zip")
    send_telegram_message(f'✅🔄 Backup done: {archive["name"]} ({size_to_human(backup_size)})')


@catch_errors
def main():
    folder_size = sum(os.path.getsize(file) for file in glob.glob(settings['backup_folder_name'] + '/**', recursive=True))
    size_limit = settings['backup_folder_size_limit']
    max_size = human_to_size(size_limit)
    if folder_size > max_size:
        logging.info('Max size reached')
        send_telegram_message(f"❌🔄 Backup failed: Max size reached {size_to_human(folder_size)} / {size_limit}")

    else:
        logging.info(size_to_human(folder_size))
        for archive in settings['backup_archives']:
            make_backup(archive)
        folder_size = sum(os.path.getsize(file) for file in glob.glob(settings['backup_folder_name'] + '/**', recursive=True))
        send_telegram_message(f'ℹ️🔄 Backups folder size: {size_to_human(folder_size)} / {size_limit}')


if __name__ == "__main__":
    main()
