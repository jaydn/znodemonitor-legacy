import os
import sys
import json
import subprocess

sys.path.append(os.path.abspath('..'))
from znconfig import config
from sendmail import send_reward_alert
from models import Node
from zcoin import ZCoinAdapter

x = config['node_args']
z = ZCoinAdapter(x['host'], x['port'], x['user'], x['password'])

def main():
#    block_count = subprocess.check_output([config['zcoincli_binary'], 'getblockcount']).decode().strip('\r\n')
    block_count = z.get_block_count()

 #   winners = subprocess.check_output([config['zcoincli_binary'], 'znode', 'winners']).decode().strip('\r\n')
 #   winners = json.loads(winners)
    winners = z.call('znode', 'winners')

    winner = winners[str(block_count)].split(':')[0]

    print('block #{0} winner {1}'.format(block_count, winner))

    res = Node.select().where((Node.node_payee == winner))

    print(len(res))

    for r in res:
        if r.user.reward_emails:
            print('sending reward email to: '+r.user.email)
            send_reward_alert(r.user.email, r.node_payee, block_count)


if __name__ == '__main__':
    main()
