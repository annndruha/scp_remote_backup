import os
import subprocess
import logging
import shutil
import json
import datetime
import dotenv

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


def catch_errors(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as err:
            logging.error(err)
    return wrapper


@catch_errors
def execute(command):
    logging.info(command)
    # try:
    process = subprocess.Popen([*command.split()], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    exit_code = process.wait()
    if exit_code != 0:
        raise subprocess.CalledProcessError(returncode=process.returncode, cmd=str(err))
    # except subprocess.CalledProcessError as err:
    #     logging.error(str(err))


def make_backup(_archive):
    if not os.path.exists('backups'):
        os.makedirs('backups')
    if not os.path.exists('temp'):
        os.makedirs('temp')

    stamp = datetime.datetime.now().strftime("%Y_%d_%m_%H_%M_%S")

    name = f'{_archive["name"]}_{stamp}'
    temp_folder = os.path.join('temp', name)

    os.makedirs(temp_folder)

    for remote_dir in _archive["remote_folders"]:
        cmd = f'scp -P {SSH_PORT} -i {SSH_PRIVATE_KEY_PATH} -r {SSH_USER}@{SSH_HOST}:{remote_dir} {temp_folder}'
        execute(cmd)

    shutil.make_archive(f'{_archive["name"]}_{stamp}', 'zip', temp_folder)
    shutil.rmtree(temp_folder)


if __name__ == "__main__":
    for archive in backup_settings['backup_archives']:
        make_backup(archive)
