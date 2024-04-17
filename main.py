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
SSH_HOST = config['SSH_HOST']
SSH_USER = config['SSH_USER']
SSH_PORT = config['SSH_PORT']
SSH_PRIVATE_KEY_PATH = config['PRIVATE_KEY_PATH']

TG_BOT_TOKEN = config['TG_BOT_TOKEN']
TG_CHAT_ID = config['TG_CHAT_ID']


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
    remote_paths = archive["remote_folders"]

    execute_remote(f'mkdir {os.path.join(os.getcwd(), temp_local_folder)}')
    for remote_dir in remote_paths:
        execute_remote(f'scp -P {SSH_PORT} -i {SSH_PRIVATE_KEY_PATH} -r {SSH_USER}@{SSH_HOST}:{remote_dir} {temp_local_folder}')
    shutil.make_archive(f'{archive["name"]}_{int(time.time())}', 'zip', temp_local_folder)
    shutil.rmtree(temp_local_folder)


