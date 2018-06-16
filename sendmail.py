import requests
import time
import html
import os

from models import User
from znconfig import config


def send_alert(node, old):
    ut = int(time.time())

    try:
        userobj = User.select().where((User.id == node.user.id))[0]
    except Exception as e:
        print(str(e))
        return

    if userobj.email_last + userobj.email_cooldown >= ut:
        return

    userobj.email_last = ut
    userobj.save()

    htmlx = """\
    <html>
    <head>
    </head>
    <body>
    <p>Your node <strong><a href="{3}">{5}</a></strong> has changed state from <strong>{1}</strong> to <strong>{2}</strong>.</p>
    <br>
    <p><b>Label: </b>{5}<br><b>IP: </b>{4}<br><b>TXID: </b>{0}</p>
    </body>
    </html>
    """.format(
            html.escape(node.txid),
            html.escape(old),
            html.escape(node.node_status),
            'https://' + config['domain'] + '/node/' + str(node.id),
            html.escape(node.node_ip),
            html.escape(node.label)
        )

    r = requests.post('https://api.mailgun.net/v3/'+config['mailgun_domain']+'/messages',
            data={
                'from': 'noreply@'+config['mailgun_domain'],
                'to': userobj.email,
                'subject': '{0} from {1} to {2}'.format(node.label, old, node.node_status),
                'html': htmlx
                },
            auth=('api', config['mailgun_key'])
        )

    print(r.status_code)
    print(r.text)


def send_pw_rst(email, token):
    htmlx = """\
    <html>
    <head>
    </head>
    <body>
    <h1>{2} password reset</h1>
    <p><a href="https://{2}/forgot/{0}/{1}">https://{2}/forgot/{0}/{1}</a></p>
    </body>
    </html>
    """.format(email, token, config['domain'])

    r = requests.post('https://api.mailgun.net/v3/'+config['mailgun_domain']+'/messages',
            data={
                'from': 'noreply@'+config['mailgun_domain'],
                'to': email,
                'subject': 'Password Reset',
                'html': htmlx
                },
            auth=('api', config['mailgun_key'])
        )

    print(r.status_code)
    print(r.text)

def send_reward_alert(email, payee, block_no):
    htmlx = """\
    <html>
    <head>
    </head>
    <body>
    <h1>{0} reward alert</h1>
    <p>One of the nodes on your account has a payee that has been listed as the winner of block #{1}'s reward.</p>
    <p>Payee: {2}</p>
    </body>
    </html>
    """.format(config['domain'], block_no, payee)

    r = requests.post('https://api.mailgun.net/v3/'+config['mailgun_domain']+'/messages',
            data={
                'from': 'noreply@'+config['mailgun_domain'],
                'to': email,
                'subject': 'Node Reward',
                'html': htmlx
                },
            auth=('api', config['mailgun_key'])
        )

    print(r.status_code)
    print(r.text)


