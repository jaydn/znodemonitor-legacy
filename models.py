from znconfig import config
import time
import peewee

db = peewee.MySQLDatabase(config['database_name'], **config['database_kvargs'])

class BaseModel(peewee.Model):
    class Meta:
        database = db

class User(BaseModel):
    email = peewee.CharField(unique=True, null=False)
    passwordhash = peewee.CharField(null=False)
    reset_token = peewee.TextField(null=True)
    reset_last = peewee.IntegerField(null=False, default=0)
    email_cooldown = peewee.IntegerField(null=False, default=300)
    email_last = peewee.IntegerField(null=False, default=0)
    timezone = peewee.TextField(null=False, default='UTC')
    reward_emails = peewee.BooleanField(null=False, default=False)

class Node(BaseModel):
    user = peewee.ForeignKeyField(User, backref='nodes', null=False)
    label = peewee.CharField(null=False)
    txid = peewee.CharField(null=False)
    node_collat_addr = peewee.CharField(null=True)
    node_status = peewee.CharField(null=True)
    node_pose_score = peewee.IntegerField(null=True)
    node_ip = peewee.CharField(null=True)
    node_last_paid_time = peewee.DateTimeField(null=True)
    node_last_paid_block = peewee.IntegerField(null=True)
    node_payout_addr = peewee.CharField(null=True)
    node_owner_addr = peewee.CharField(null=True)
    node_voting_addr = peewee.CharField(null=True)
    node_protx_hash = peewee.CharField(null=True)
    node_oper_pubkey = peewee.CharField(null=True)
    node_oper_reward = peewee.CharField(null=True)

class State(BaseModel):
    key = peewee.CharField(null=False)
    value = peewee.CharField()

if __name__ == '__main__':
    with db:
        db.create_tables([User, Node, State])
        State.create(key='last_updated', value=int(time.time())).save()
