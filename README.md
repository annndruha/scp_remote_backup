# SCP Remote Backup (Ubuntu)
Script for pull some folders/files from another server and zip it as backup. Also send a telegram message about succeed/fail backup.

# Install and setup

* Clone repo
  ```bash
  git clone https://github.com/annndruha/scp_remote_backup.git && cd scp_remote_backup
  ```

* Create venv
  ```bash
  python3 -m venv venv && venv/bin/python3 -m pip install -r requirements.txt
  ```

* Copy configs to repository root directory:
  ```bash
  cp -t . config_examples/.env config_examples/backup_folders.json
  ```

* Change `.env`-file with you tokens and specify remote folders needs to backup in `backup_folders.json`.

## First time
* Make sure that private key is correct permissions like `-r--------`. Change permissions if needed: 
  ```bash
  chmod 400 ~/.ssh/private_key
  ```

* For new servers check that ssh/scp connections is added to known_host, or just connect first time manually:
  ```bash
  ssh -p 22 -i ~/.ssh/private_key -r user@my.example.com
  ```

* Run script manually:
  ```bash
  venv/bin/python3 main.py
  ```
* Check backup archive and make shure that all is ok.

## Scheduling

* Script scheduling via cron. Edit cronfile:
  ```bash
  crontab -e
  ```
* Paste this line to end of cronfile, where `/workdir` is path to cloned repo. Next example is every day at 00:00 backup [More examples](https://crontab.guru/examples.html). :
  ```text
  0 0 * * * cd /workdir && venv/bin/python3 main.py >> /workdir/logs.txt 2>&1
  ```
