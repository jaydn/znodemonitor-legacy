import json
import os

_CONFIG_FILE_PATH = os.path.expanduser('~/znodemonitor_config.json')

config = {
    "config_name": "default",
    "domain": "znodemonitor.com",
    "secret": "mash your keyboard into this or people will hack your site",
    "database_name": "znodemonitor",
    "database_kvargs": {
        "user": "znodemonitor",
        "password": "password",
        "host": "localhost",
        "port": 3306,
    },
    "show_dev_credit": True,
    "enforce_limit": True,
    "limit": 25,
    "zcoincli_binary": "~/zcoin-0.13.6/bin/zcoin-cli",
    "enforce_invite": True,
    "invite": "your_invite_key",
    "mailgun_domain": "znodemonitor.com",
    "mailgun_key": "xxxxx"
}


if os.path.exists(_CONFIG_FILE_PATH):
    with open(_CONFIG_FILE_PATH, mode='r') as handle:
        config = json.load(handle)

config['zcoincli_binary'] = os.path.expanduser(config['zcoincli_binary'])
