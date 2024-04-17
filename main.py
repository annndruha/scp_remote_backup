import os
import time
import subprocess
from dotenv import dotenv_values
import logging
import shutil
import json

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

config = dotenv_values('.env')
IP_OR_DOMAIN = config['IP_OR_DOMAIN']
USER = config['USER']
PORT = config['PORT']
TG_BOT_TOKEN = config['TG_BOT_TOKEN']
TG_CHAT_ID = config['TG_CHAT_ID']
PRIVATE_KEY_PATH = config['PRIVATE_KEY_PATH']


def execute_remote(command):
    logging.info(command)
    try:
        process = subprocess.Popen([*command.split()], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        exit_code = process.wait()
        if exit_code != 0:
            raise subprocess.CalledProcessError(returncode=process.returncode, cmd=str(err))
    except subprocess.CalledProcessError as err:
        logging.error(str(err))


with open('backup_folders.json') as f:
    backup_settings = json.load(f)

for archive in backup_settings['backup_archives']:
    temp_local_folder = f'temp_{archive["name"]}_{int(time.time())}'
    remote_paths = archive["folders"]

    execute_remote(f'mkdir {os.path.join(os.getcwd(), temp_local_folder)}')
    for remote_dir in remote_paths:
        execute_remote(f'scp -P {PORT} -i {PRIVATE_KEY_PATH} -r {USER}@{IP_OR_DOMAIN}:{remote_dir} {temp_local_folder}')
    shutil.make_archive(f'{archive["name"]}_{int(time.time())}', 'zip', temp_local_folder)
    shutil.rmtree(temp_local_folder)

# === SCRIPT SHEDULLED BY CRON
# === edit cronfile:
# crontab -e
# === Add this line to cronfile:
# * * * * * cd /workdir && /workdir/venv/bin/python3 main.py >> /workdir/logs.txt 2>&1
