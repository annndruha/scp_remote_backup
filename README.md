# SCP Remote Backup [IN DEVELOPMENT]
Script for pull and zip folders from another server.

# Install (Ubuntu)

**Clone and configs**

Clone repo
```bash
git clone https://github.com/annndruha/scp_remote_backup.git && cd scp_remote_backup
```

Create venv
```bash
python3 -m venv venv && venv/bin/python3 -m pip install -r requirements.txt
```

Copy configs to repository root directory:

```bash
cp -t . config_examples/.env config_examples/backup_folders.json
```

Change configs values with you tokens and remote backup folders.

**Make sure that private key is correct permissions**

Correct permissions: `-r--------`

```bash
chmod 400 ~/.ssh/private_key
```

**Known hosts**

For new remote servers check that ssh/scp connections is added to known_host, or just connect first time manually:

```bash
ssh -p 22 -i ~/.ssh/private_key -r user@my.example.com
```

**Manual test**

```bash
venv/bin/python3 main.py
```

**Script scheduling via cron**

Edit cronfile:
```bash
bashcrontab -e
```

[Time periods examples](https://crontab.guru/examples.html). Next example is every day backup:

```text
0 0 * * * cd /workdir && venv/bin/python3 main.py >> /workdir/logs.txt 2>&1
```