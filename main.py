import os
import subprocess
import logging
import shutil
import json
import datetime
import dotenv
import requests

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

config = dotenv.dotenv_values('.env')
SSH_HOST = config['SSH_HOST']
SSH_USER = config['SSH_USER']
SSH_PORT = config['SSH_PORT']
SSH_PRIVATE_KEY_PATH = config['SSH_PRIVATE_KEY_PATH']

TG_BOT_TOKEN = config['TG_BOT_TOKEN']
TG_CHAT_ID = config['TG_CHAT_ID']

with open('backup_folders.json') as f:
    backup_settings = json.load(f)
    # Settings asserts

TEMP = 'temp'
BACKUP_FOLDER = 'backups'


def send_telegram_message(msg: object):
    msg = str(msg)
    if not len(msg):
        return

    logging.info(f'[Send message] {msg}')
    r = requests.post(f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
                      f'?parse_mode=HTML&chat_id={TG_CHAT_ID}&text={msg}',timeout=10)
    if r.status_code != 200:
        logging.error(f'[Telegram error] {r.status_code}, {r.text}')


def catch_errors(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as err:
            logging.error(err)
            send_telegram_message('❌🔄 Backup failed: ' + str(err))
    return wrapper


def execute(command):
    logging.info('[Run command] ' + str(command))
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = process.wait()
    out, err = process.communicate()
    if exit_code != 0:
        raise subprocess.CalledProcessError(returncode=process.returncode, cmd=str(err))


@catch_errors
def make_backup(_archive):
    send_telegram_message('▶️🔄 Starting backup: ' + _archive["name"])

    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
    if not os.path.exists(TEMP):
        os.makedirs(TEMP)

    stamp = datetime.datetime.now().strftime("%Y_%d_%m_%H_%M_%S")
    name = f'{_archive["name"]}_{stamp}'
    temp_folder = os.path.join(TEMP, name)
    os.makedirs(temp_folder)

    for remote_dir in _archive["remote_folders"]:
        cmd = f'scp -r -P {SSH_PORT} -i {SSH_PRIVATE_KEY_PATH} {SSH_USER}@{SSH_HOST}:{remote_dir} {temp_folder}'
        execute(cmd)

    archive_name = os.path.join(BACKUP_FOLDER, f'{_archive["name"]}_{stamp}')
    shutil.make_archive(archive_name, 'zip', temp_folder)
    shutil.rmtree(temp_folder)

    send_telegram_message('✅🔄 Backup successful: ' + _archive["name"])


if __name__ == "__main__":
    for archive in backup_settings['backup_archives']:
        make_backup(archive)
