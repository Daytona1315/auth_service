from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    nickname = fields.CharField(max_length=255, null=True)
    avatar = fields.CharField(max_length=255, null=True)
    confirmed = fields.BooleanField(default=False)

    credentials_local = fields.ReverseRelation["CredentialsLocal"]
    credentials_google = fields.ReverseRelation["CredentialsGoogle"]
    credentials_facebook = fields.ReverseRelation["CredentialsFacebook"]

    class Meta:
        table = 'users'


class CredentialsLocal(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='credentials_local', on_delete=fields.CASCADE)
    login = fields.CharField(max_length=255, unique=True)  # login is same as email
    password = fields.CharField(max_length=255)
    version = fields.IntField(default=1)
    last_password = fields.CharField(max_length=255, null=True)

    class Meta:
        table = 'credentials_local'


class CredentialsGoogle(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='credentials_google', on_delete=fields.CASCADE)
    google_user_id = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = 'credentials_google'


class CredentialsFacebook(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='credentials_facebook', on_delete=fields.CASCADE)
    facebook_user_id = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = 'credentials_facebook'
