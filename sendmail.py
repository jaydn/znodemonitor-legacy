import requests
import time
import html
import os
from models import User, Node
from znconfig import config
from jinja2 import Environment, FileSystemLoader

def cooldown_user(userobj):
    ut = int(time.time())

    if userobj.email_last + userobj.email_cooldown >= ut:
        return True

    userobj.email_last = ut
    userobj.save()

    return False

templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
env = Environment(loader = FileSystemLoader(templates_dir))

def send_score_increase_alert(node, old_score):
    try:
        try:
            userobj = User.select().where((User.id == node.user.id))[0]
        except Exception as e:
            print(str(e))
            return

        if cooldown_user(userobj):
            return
        
        template = env.get_template('score_increase_alert.html')

        htmlx = template.render(node=node, old_score=old_score, domain=config['domain'])

        r = requests.post('https://api.mailgun.net/v3/'+config['mailgun_domain']+'/messages',
                data={
                    'from': 'noreply@'+config['mailgun_domain'],
                    'to': userobj.email,
                    'subject': f'{node.label} increased score to {node.node_pose_score}',
                    'html': htmlx
                    },
                auth=('api', config['mailgun_key'])
            )

        print(r.status_code)
        print(r.text)
    except Exception as e:
        print('I FAILED TO SEND AN EMAIL')
        print(str(e))
        print(str(node), str(old))

def send_status_change_alert(node, old):
    try:
        try:
            userobj = User.select().where((User.id == node.user.id))[0]
        except Exception as e:
            print(str(e))
            return

        if cooldown_user(userobj):
            return
        

        template = env.get_template('status_change_alert.html')

        htmlx = template.render(node=node, old_status=old, domain=config['domain'])

        r = requests.post('https://api.mailgun.net/v3/'+config['mailgun_domain']+'/messages',
                data={
                    'from': 'noreply@'+config['mailgun_domain'],
                    'to': userobj.email,
                    'subject': f'{node.label} from {old} to {node.node_status}',
                    'html': htmlx
                    },
                auth=('api', config['mailgun_key'])
            )

        print(r.status_code)
        print(r.text)
    except Exception as e:
        print('I FAILED TO SEND AN EMAIL')
        print(str(e))
        print(str(node), str(old))

if __name__ == "__main__":
    nodeobj = Node.select().where((Node.id == 28))[0]
    print(nodeobj.label)
    send_status_change_alert(nodeobj, 'ENABLED')
    send_score_increase_alert(nodeobj, 9999)


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


