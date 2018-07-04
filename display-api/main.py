import time
import json
import subprocess
import re
import flask
import flask_restful
import flask_cors
from webargs import fields, validate
from webargs.flaskparser import use_args
from playhouse.shortcuts import model_to_dict
from werkzeug.security import check_password_hash, generate_password_hash
import flask_jwt_extended
import os
import sys
sys.path.append(os.path.abspath('..'))
from sendmail import send_pw_rst
from models import User, Node, db
from znconfig import config

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '123875213865'
flask_cors.CORS(app)
api = flask_restful.Api(app)
jwt = flask_jwt_extended.JWTManager(app)

auth_args = {
   'email': fields.Str(required=True, validate=validate.Length(min=2, max=256)),
   'password': fields.Str(required=True, validate=validate.Length(min=12, max=256)),
}

@app.route('/auth', methods=['POST'])
@use_args(auth_args)
def jwt_auth(args):
    try:
        u = User.select().where((args['email'] == User.email))[0]
    except:
        return flask.jsonify({'msg': 'Invalid email or password.'})

    if check_password_hash(u.passwordhash, args['password']):
        return flask.jsonify({'token': flask_jwt_extended.create_access_token(identity=u.id, expires_delta=False)})

    return flask.jsonify({'msg': 'Invalid email or password.'})


@app.route('/statistics', methods=['GET'])
def stats():
    try:
        obj = json.loads(subprocess.check_output([config['zcoincli_binary'], 'getinfo']).decode())
    except:
        pass

    version = obj.get('version', None)
    height = obj.get('blocks', None)

    try:
        obj = json.loads(subprocess.check_output([config['zcoincli_binary'], 'znodelist']).decode())
    except:
        pass

    nodes = len(obj)

    state_count = {}
    for k,v in obj.items():
        state_count[v] = state_count.get(v, 0) + 1
    
    return flask.jsonify({'version': version, 'height': height, 'nodes': nodes, 'state_count': state_count})


@app.route('/info/register', methods=['GET'])
def info_register():
    return flask.jsonify({
        'inviteRequired': config['enforce_invite']
        })

class Register(flask_restful.Resource):
    reg_args = {
        'invkey': fields.Str(),
        'email': fields.Str(required=True, validate=validate.Length(min=2, max=256)),
        'password': fields.Str(required=True, validate=validate.Length(min=12, max=256)),
    }

    @use_args(reg_args)
    def post(self, args):
        if config['enforce_invite']:
            if args.get('invkey', None) != config['invite']:
                return {'msg': 'Invalid invite key.'}
        passhash = generate_password_hash(args['password'], method='pbkdf2:sha256')
        u = User.create(email=args['email'], passwordhash=passhash, email_cooldown=300)
        return {'token': flask_jwt_extended.create_access_token(identity=u.id, expires_delta=False)}

def without_keys(d, *keys):
    return dict(filter(lambda key_value: key_value[0] not in keys, d.items()))


def add_node(user, lbl, txid, idx):
    print(user, lbl, txid, idx)
    if len(user.nodes) >= config['limit'] and config['enforce_limit']:
        return
    n = Node.create(user=user, label=lbl, txid=(txid + ', ' + str(idx)))
    print(n.id)

class Settings(flask_restful.Resource):
    method_decorators = [flask_jwt_extended.jwt_required]

    settings_args = {
        'cooldown': fields.Integer(required=True, validate=lambda val: val >= 0 and val <= 86400),
        'emailReward': fields.Bool(),
    }

    def get(self):
        uid = flask_jwt_extended.get_jwt_identity()
        u = User.select().where((User.id == uid))[0]
        return {'cooldown': u.email_cooldown, 'emailReward': u.reward_emails}
    
    @use_args(settings_args)
    def post(self, args):
        uid  = flask_jwt_extended.get_jwt_identity()
        u = User.select().where((User.id == uid))[0]
        u.email_cooldown = args['cooldown']
        u.reward_emails = args['emailReward']
        u.save()
        return {}, 200


@app.route('/getnode/<int:nid>')
@flask_jwt_extended.jwt_required
def getnode(nid):
    uid = flask_jwt_extended.get_jwt_identity()
    try:
        res = Node.select().join(User).where((User.id == uid) & (Node.id == nid))[0]
    except:
        return flask.abort(403)
    try:
        res.node_last_seen = time.mktime(row.node_last_seen.timetuple())
        res.node_last_paid_time = time.mktime(row.node_last_paid_time.timetuple())
    except:
        res.node_last_seen = 0
        res.node_last_paid_time = 0

    d = without_keys(model_to_dict(res), 'user')
    return flask.jsonify(d)

class Nodes(flask_restful.Resource):
    method_decorators = [flask_jwt_extended.jwt_required]

    def get(self):
        uid = flask_jwt_extended.get_jwt_identity()
        res = Node.select().join(User).where((User.id == uid))
        real_res = []
        for row in res:
            try:
                row.node_last_seen = time.mktime(row.node_last_seen.timetuple())
                row.node_last_paid_time = time.mktime(row.node_last_paid_time.timetuple())
            except:
                row.node_last_seen = 0
                row.node_last_paid_time = 0
            real_res.append(row)
        return [without_keys(model_to_dict(x), 'user') for x in real_res]

    def post(self):
        uid = flask_jwt_extended.get_jwt_identity()

        users_nodes = len(Node.select(Node, User).join(User).where((User.id == uid)))
        if users_nodes >= config['limit'] and config['enforce_limit']:
            return {'msg': "You've hit the {0} node limit.".format(config['limit'])}, 403

        u = User.select().where((User.id==uid))[0]

        to_add = flask.request.get_json()

        if type(to_add) != list:
            print(type(to_add))
            print(to_add)
            return {}, 403

        for line in to_add:
            try:
                lbl = line['label']
                if not re.match(r'^.{1,32}$', lbl):
                    continue
                print(lbl)

                txid = line['txid']
                if not re.match(r'^[a-z0-9]{64}$', txid):
                    continue
                print(txid)

                idx = line['idx']
                if not re.match(r'^\d+$', idx):
                    continue
                idx = int(idx)
                if idx < 0:
                    continue
                if idx > 9999:
                    continue

                add_node(u, lbl, txid, idx)
            except Exception as e:
                print(str(e))
                continue


class NodeDelete(flask_restful.Resource):
    method_decorators = [flask_jwt_extended.jwt_required]

    def post(self):
        uid = flask_jwt_extended.get_jwt_identity()
        x = flask.request.get_json()
        if type(x) != list:
            return {}, 403
        for row in x:
            try:
                row = int(row)
                n = Node.select().join(User).where((Node.id == row) & (User.id == uid))[0]
                n.delete_instance()
            except:
                continue

api.add_resource(Register, '/register')
api.add_resource(Nodes, '/nodes')
api.add_resource(NodeDelete, '/delete') #need to get delete method working
api.add_resource(Settings, '/settings')

def main():
    app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
    main()
