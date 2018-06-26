import flask
import flask_restful
from webargs import fields, validate
from webargs.flaskparser import use_args
from playhouse.shortcuts import model_to_dict

import os
import sys
sys.path.append(os.path.abspath('..'))
from sendmail import send_pw_rst
from models import User, Node, db
from znconfig import config

app = flask.Flask(__name__)
api = flask_restful.Api(app)

class Register(flask_restful.Resource):
    register_args = {
        'username': fields.Str(required=True, validate=validate.Length(min=2, max=16)),
        'password': fields.Str(required=True, validate=validate.Length(min=12, max=256)),
    }

    @use_args(register_args)
    def post(self, args):
        return {'status': 'ok'}

api.add_resource(Register, '/register')

def main():
    app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
    main()
