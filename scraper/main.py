import subprocess
import datetime
import shlex
import json
import time
import sys
import os

sys.path.append(os.path.abspath('..'))
from sendmail import send_alert
from models import User, Node
from znconfig import config
from zcoin import ZCoinAdapter

x = config['node_args']
z = ZCoinAdapter(x['host'], x['port'], x['user'], x['password'])

def znode_list():
    '''
        evoznodelist
        ---------
        proTxHash
        address
        payee
        status
        lastpaidtime
        lastpaidblock
        owneraddress
        votingaddress
        collateraladdress
        pubkeyoperator

        protx list registered true
        ---------
        proTxHash
        collateralHash
        collateralIndex
        collateralAddress
        operatorReward
        state
        confirmations
        wallet
        service
        registeredHeight
        lastPaidHeight
        PoSePenalty
        PoSeRevivedHeight
        PoSeBanHeight
        revocationReason
        ownerAddress
        votingAddress
        payoutAddress
        pubKeyOperator

    '''
    combined_list = {}

    evoznodelist = z.call('evoznodelist')
    combined_list = {k.replace('COutPoint', '').strip('()\r\n'): v for k,v in evoznodelist.items()}

    protx_list = z.call('protx', 'list', 'registered', 'true')
    for _ in protx_list:
        for k,v in _.items():
            try:
                combined_list[f"{_['collateralHash']}, {_['collateralIndex']}"][k] = v
            except Exception as e:
                print(f"Choked on {k}: {v} ({str(e)})")
                continue

    
    #print(combined_list['068e316808d91a6ea4e350d8792d7b87025ded6a48f2a01773332afec76fb5c5, 5'])

    return combined_list
    # for k,v in combined_list.items():
    #     print(k)
    #     print('----------')
    #     print(v)
    #     print('')



    

#    b = json.loads(obj)
#    print(str(b))
    #return {tx[10:-1]: shlex.split(data) for tx,data in obj.items()}

znode_list()

def is_synced():
    obj = z.call('evoznsync', 'status')
    #print(obj)
    #obj = json.loads(subprocess.check_output([config['zcoincli_binary'], 'znsync', 'status']).decode())
    return 'AssetID' in obj and obj['AssetID'] == 999

def main(should_send_mail):
    if not is_synced():
        print('List is not synced (AssetID != 999)')
        return

    cache = znode_list()

    all_nodes = Node.select()

    alerts = []

    for node in all_nodes:
#        print(node.txid)
        try:
            node_result = cache[node.txid]
            #print(str(node_result))
        except:
            node_result = {}
        
        should_alert = False

        old_status = node.node_status
        if node_result.get('status', 'NOT_ON_LIST') != old_status and old_status != None:
            should_alert = True
#            print('{2} : {1} -> {0}'.format(node_result[NODE_STATUS], node.node_status, node.user.email))
    
        node.node_collat_addr     = node_result.get('collateralAddress', None)
        node.node_status          = node_result.get('status', 'NOT_ON_LIST')
        node.node_pose_score      = node_result.get('state', {}).get('PoSePenalty', None)
        node.node_ip              = node_result.get('state', {}).get('service', None)
        node.node_last_paid_time  = None if node_result.get('lastpaidtime', 0) == 0 else datetime.datetime.fromtimestamp(int(node_result['lastpaidtime']))
        node.node_last_paid_block = node_result.get('lastpaidblock', None)
        node.node_payout_addr     = node_result.get('state', {}).get('payoutAddress', None)
        node.node_owner_addr      = node_result.get('state', {}).get('ownerAddress', None)
        node.node_voting_addr     = node_result.get('state', {}).get('votingAddress', None)
        node.node_protx_hash      = node_result.get('proTxHash', None)
        node.node_oper_pubkey     = node_result.get('state', {}).get('pubKeyOperator', None)
        node.node_oper_reward     = node_result.get('operatorReward')
        
        node.save()

        if should_alert:
            alerts.append((node, old_status))

    print('Processed {0} nodes, sending {1} emails'.format(len(all_nodes), len(alerts)))

    for alert in alerts:
        if should_send_mail:
            send_alert(*alert)
        else:
            print('would send mail')
        print(*alert)



if __name__ == '__main__':
    send_mail = True
    cron_mode = False
    for arg in sys.argv:
        if arg == 'no_send_mail':
            send_mail = False
        if arg == 'cron_mode':
            cron_mode = True



    while True:
        print('starting loop' + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
        main(send_mail)
        print('ending loop' + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
        if cron_mode:
            break
        time.sleep(30)

