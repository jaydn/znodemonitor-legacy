from znconfig import config
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
    node_status = peewee.CharField(null=True)
    node_protocol = peewee.IntegerField(null=True)
    node_payee = peewee.CharField(null=True)
    node_last_seen = peewee.DateTimeField(null=True)
    node_active_seconds = peewee.IntegerField(null=True)
    node_last_paid_time = peewee.DateTimeField(null=True)
    node_last_paid_block = peewee.IntegerField(null=True)
    node_ip = peewee.CharField(null=True)

if __name__ == '__main__':
    with db:
        db.create_tables([User, Node])
