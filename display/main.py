from validate_email import validate_email
from random import SystemRandom
import dateutil.relativedelta
import playhouse.shortcuts
import werkzeug.security
import functools
import string
import flask
import json
import pytz
import time
import uuid
import sys
import os
import re

sys.path.append(os.path.abspath('..'))
from sendmail import send_pw_rst
from models import User, Node, db
from znconfig import config
from zcoin import ZCoinAdapter

z = (lambda x: ZCoinAdapter(x['host'], x['port'], x['user'], x['password']))(config['node_args'])

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = config['secret']

@app.before_request
def connect_db():
    if db.is_closed():
        db.connect()

@app.teardown_request
def close_db(pad):
    if not db.is_closed():
        db.close()


#TODO: wtf
def access_only(usertype):
    def real_dec(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if usertype == 'auth':
                if 'UserID' not in flask.session:
                    return flask.redirect(flask.url_for('.index'))
            elif usertype == 'unauth':
                if 'UserID' in flask.session:
                    return flask.redirect(flask.url_for('.index'))
            else:
                raise Exception("!! bad auth decorator")

            return func(*args, **kwargs)
        return wrapper
    return real_dec


@app.context_processor
def inject_config():
    return {'config': config}

@app.template_filter('tz_localize')
def tz_localize_filter(s):
    user = User.select().where((User.id == flask.session['UserID']))[0]
    try:
        utctz = pytz.timezone('UTC')
        tz = pytz.timezone(user.timezone)
        return utctz.localize(s).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ''

@app.template_filter('secs_humanize')
def secs_humanize_filter(s):
    try:
        return '{0.days}d {0.hours}h'.format(dateutil.relativedelta.relativedelta(seconds=s))
    except:
        return ''

@app.route('/')
def index():
    return flask.redirect(flask.url_for('overview' if 'UserID' in flask.session else 'login'))

#need to cache this one, easy dos
@app.route('/statistics', methods=['GET'])
#@access_only('auth')
def statistics():
    try:
        obj = z.call('getinfo')
    except Exception as e:
        return flask.render_template('statistics_offline.html', exception_msg=str(e))

    version = obj.get('version', None)
    height = obj.get('blocks', None)

    try:
        obj = z.call('znodelist')
    except:
        return flask.render_template('statistics_offline.html', exception_msg=str(e))

    nodes = len(obj)

    state_count = {}
    for k,v in obj.items():
        state_count[v] = state_count.get(v, 0) + 1

    return flask.render_template('statistics.html', version=version, height=height, nodes=nodes, states=state_count)

@app.route('/register', methods=['GET', 'POST'])
@access_only('unauth')
def register():
    if flask.request.method == 'POST':
        form_vals = {'emailaddr', 'password', 'passwordv'}
        if config['enforce_invite']:
            form_vals.add('invitekey')
        if form_vals != set(flask.request.form):
            return flask.render_template('register.html', issues=['Please submit a valid form.'])
        issues = []

        if config['enforce_invite']:
            if flask.request.form['invitekey'] != config['invite']:
                issues.append('Invite key is wrong.')

        if flask.request.form['password'] != flask.request.form['passwordv']:
            issues.append('Password does not match confirmation.')

        if len(flask.request.form['password']) < 8:
            issues.append('Password must be longer than 8 chars.')

        if len(flask.request.form['password']) > 256:
            issues.append('Password must be shorter than 256 chars.')

        if not validate_email(flask.request.form['emailaddr']):
            issues.append('Invalid email.')

        if len(User.select().where((User.email==flask.request.form['emailaddr']))) != 0:
            issues.append('Email is taken.')

        if len(issues) != 0:
            return flask.render_template('register.html', issues=issues)
        else:
            passhash = werkzeug.security.generate_password_hash(flask.request.form['password'], method='pbkdf2:sha256')
            u = User.create(email=flask.request.form['emailaddr'], passwordhash=passhash, timezone='UTC', email_cooldown=300)
            flask.session['UserID'] = u.id
            return flask.redirect(flask.url_for('overview'))
    elif flask.request.method == 'GET':
        return flask.render_template('register.html')

@app.route('/forgot/<string:email>/<string:token>', methods=['GET', 'POST'])
@access_only('unauth')
def forgots2(email, token):
    try:
        u = User.select().where((User.email==email))[0]
    except:
        return flask.abort(404)

    if u.reset_token != token:
        return flask.abort(403)

    if flask.request.method == 'GET':
        return flask.render_template('forgots2.html', email=email)
    elif flask.request.method == 'POST':
        if len(flask.request.form) != 2:
            return flask.render_template('forgots2.html', issues=['Please submit a valid form.'])
        if {'password', 'passwordv'} != set(flask.request.form):
            return flask.render_template('forgots2.html', issues=['Please submit a valid form.'])
        issues = []
        if flask.request.form['password'] != flask.request.form['passwordv']:
            issues.append('Password does not match confirmation.')
        if len(flask.request.form['password']) < 8:
            issues.append('Password must be longer than 8 chars.')
        if len(flask.request.form['password']) > 256:
            issues.append('Password must be shorter than 256 chars.')
        if len(issues) != 0:
            return flask.render_template('forgots2.html', issues=issues)
        else:
            passhash = werkzeug.security.generate_password_hash(flask.request.form['password'], method='pbkdf2:sha256')
            u.passwordhash = passhash
            u.reset_token = None
            u.save()
            return flask.redirect(flask.url_for('index'))
            


@app.route('/forgot', methods=['GET', 'POST'])
@access_only('unauth')
def forgot():
    if flask.request.method == 'GET':
        return flask.render_template('forgot.html')
    else:
        if {'emailaddr'} != set(flask.request.form):
            return flask.render_template('forgot.html', issues=['Please submit a valid form.'])

        try:
            u = User.select().where((User.email == flask.request.form['emailaddr']))[0]
        except:
            return flask.render_template('forgot.html', issues=['Email not found.'])

        ut = int(time.time())

        if u.reset_last + 3600 >= ut:
            return flask.render_template('forgot.html', issues=['Please wait before requesting another password reset.'])

        secrand = SystemRandom()
        u.reset_token = str(''.join(secrand.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(255)))
        u.reset_last = ut
        u.save()

        send_pw_rst(u.email, u.reset_token)
        return flask.redirect(flask.url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
@access_only('unauth')
def login():
    if flask.request.method == 'POST':
        if {'emailaddr', 'password'} != set(flask.request.form):
            return flask.render_template('login.html', issues=['Please submit a valid form.'])
        try:
            u = User.select().where((User.email==flask.request.form['emailaddr']))[0]
        except:
            return flask.render_template('login.html', issues=['Email or password incorrect.'])

        if werkzeug.security.check_password_hash(u.passwordhash, flask.request.form['password']):
            flask.session['UserID'] = u.id
            return flask.redirect(flask.url_for('overview'))
        else:
            return flask.render_template('login.html', issues=['Email or password incorrect.'])
    elif flask.request.method == 'GET':
        return flask.render_template('login.html')

@app.route('/logout', methods=['POST'])
@access_only('auth')
def logout():
    flask.session.pop('UserID', None)
    return flask.redirect(flask.url_for('index'))


def without_keys(d, *keys):
    return dict(filter(lambda key_value: key_value[0] not in keys, d.items()))

@app.route('/api/get_nodes', methods=['GET'])
def api_get_nodes():
    if 'UserID' not in flask.session:
        return flask.abort(404)
    raw_results = Node.select().join(User).where((User.id==flask.session['UserID']))
    json_this = [without_keys(playhouse.shortcuts.model_to_dict(n), "user") for n in raw_results]

    return json.dumps(json_this, default=str)

@app.route('/overview', methods=['GET'])
@access_only('auth')
def overview():
    nodelist = Node.select().where((Node.user == flask.session['UserID']))
    results = []
    enabled = 0
    attention = 0

    for node in nodelist:
        if node.node_status == 'ENABLED':
            enabled = enabled + 1
        else:
            attention = attention + 1

    return flask.render_template('overview.html', nodes=nodelist, enabled=enabled, attention=attention)

@app.route('/settings', methods=['GET', 'POST'])
@access_only('auth')
def settings():
    user = User.select().where((User.id == flask.session['UserID']))[0]
    if flask.request.method == 'GET':
        return flask.render_template('settings.html', row=user, timezones=pytz.all_timezones)
    elif flask.request.method == 'POST':
        #not happy about this one
#        if {'cooldown', 'timezone'} != set(flask.request.form):
#            return flask.render_template('settings.html', row=user, timezones=pytz.all_timezones, issues=['Please submit a valid form.'])

        if flask.request.form.get('timezone', None) not in pytz.all_timezones:
            return flask.render_template('settings.html', row=user, timezones=pytz.all_timezones, issues=['Please submit a valid form.'])

        try:
            cooldown = int(flask.request.form['cooldown'])
        except:
            return flask.render_template('settings.html', row=user, timezones=pytz.all_timezones, issues=['Please submit a valid form.'])

        if cooldown < 0 or cooldown > 84600:
            return flask.render_template('settings.html', row=user, timezones=pytz.all_timezones, issues=['Cooldown must be between 0 and 84600.'])

        rewards = bool(flask.request.form.get('rewards', False))

        user.email_cooldown = cooldown
        user.email_last = 0
        user.timezone = flask.request.form['timezone']
        user.reward_emails = rewards
        user.save()
        
        return flask.render_template('settings.html', row=user, timezones=pytz.all_timezones)

@app.route('/node/<int:nid>', methods=['GET'])
@access_only('auth')
def node(nid):
    try:
        n = Node.select().join(User).where((Node.id == nid) & (User.id==flask.session['UserID']))[0]
    except:
        return flask.abort(404)
    return flask.render_template('node.html', node=n)

def add_node(user, lbl, txid, idx):
    if len(user.nodes) >= config['limit'] and config['enforce_limit']:
        return
    n = Node.create(user=user, label=lbl, txid=(txid + ', ' + idx))
    
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'UserID' not in flask.session:
        return flask.abort(404)
#    if Node.query.filter_by(user=flask.session['UserID']).count() > 24 and not IS_IN_DEV_MODE:
    users_nodes = len(Node.select(Node, User).join(User).where((User.id == flask.session['UserID'])))
    if users_nodes >= config['limit'] and config['enforce_limit']:
        return flask.render_template('limit.html')

    if flask.request.method == 'GET':
        return flask.render_template('add.html')
    elif flask.request.method == 'POST':
        if {'nodes'} != set(flask.request.form):
            return flask.render_template('add.html', issues=['Did not receive a list. Malformed?'])
        
        u = User.select().where((User.id==flask.session['UserID']))[0]

        to_add = [k.strip('\r\n ') for k in flask.request.form['nodes'].split('\n')]
        issues = []
        
        for line in to_add:
            ret = re.match(r'^(.+) ([a-z0-9]{64}) ([0-9]+)$', line)

            lbl = None
            txid = None
            index = None
            try:
                lbl = ret.group(1)
                txid = ret.group(2)
                index = ret.group(3)
            except:
                continue

            try:
                add_node(u, lbl, txid, index)
            except:
                continue
        
        if len(issues) > 0:
            return flask.render_template('add.html', issues=list(set(issues)))
        else:
            return flask.redirect(flask.url_for('overview'))

@app.route('/api/remove', methods=['POST'])
def bremove():
    if 'UserID' not in flask.session:
        return flask.abort(404)
    if {'nodes'} != set(flask.request.form):
        return flask.abort(404)
    try:
        nodes = [int(k) for k in flask.request.form['nodes'].split(',')]
    except:
        return flask.abort(404)
    for node in nodes:
        try:
            node_obj = Node.select().join(User).where((Node.id==node) & (User.id == flask.session['UserID']))[0]
        except:
            flask.abort(403)
        node_obj.delete_instance()
        
    return ''


@app.route('/remove', methods=['GET', 'POST'])
def remove():
    if 'UserID' not in flask.session:
        return flask.abort(404)
    nodelist = Node.select().where((Node.user == flask.session['UserID']))
    return flask.render_template('remove.html', nodes=nodelist)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
