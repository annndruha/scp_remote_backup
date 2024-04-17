# SCP Remote Backup [IN DEVELOPMENT]
Script for pull and zip folders from another server.

# Init

Clone repo
```bash
git clone https://github.com/annndruha/scp_remote_backup.git
cd scp_remote_backup
```

Copy config to repository root directory:

```bash
cp config_examples/.env .
cp config_examples/backup_folders.json .
```

Change configs values with you tokens and remote backup folders.


# Script scheduling via cron (Ubuntu)

Edit cronfile:
```bash
bashcrontab -e
```

[Time periods examples](https://crontab.guru/examples.html). Next example is every day backup:

```text
0 0 * * * cd /workdir && python3 main.py >> /workdir/logs.txt 2>&1
```