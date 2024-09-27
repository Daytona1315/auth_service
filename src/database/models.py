from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=30)
    username = fields.CharField(max_length=30)
    avatar = fields.CharField(max_length=300)
    creation_date = fields.DatetimeField(auto_now=True)
    confirmed = fields.BooleanField(default=False)

    class Meta:
        table = 'users'


class CredentialsLocal(Model):
    user_id = fields.IntField()
    username = fields.CharField(max_length=30)
    hash_password = fields.CharField(max_length=256)
    last_password = fields.CharField(max_length=256)

    class Meta:
        table = 'credentials_local'


class CredentialsGoogle(Model):
    user_id = fields.IntField()
    google_user_id = fields.IntField()

    class Meta:
        table = 'credentials_google'
