from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from uuid_utils.compat import uuid7
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='User',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('uuid', fields.UUIDField(default=uuid7, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(db_index=True, auto_now=True, auto_now_add=False)),
                ('username', fields.CharField(unique=True, db_index=True, description='用户名称', max_length=20)),
                ('nick_name', fields.CharField(default='', description='昵称', max_length=50)),
                ('rank_title', fields.CharField(default='', description='称号', max_length=50)),
                ('email', fields.CharField(unique=True, db_index=True, description='邮箱', max_length=255)),
                ('password', fields.CharField(null=True, description='密码', max_length=128)),
                ('is_admin', fields.BooleanField(default=False, db_index=True, description='admin')),
                ('last_login', fields.DatetimeField(null=True, description='最后登录时间', auto_now=False, auto_now_add=False)),
                ('login_count', fields.IntField(default=0, description='登录次数')),
            ],
            options={'table': 'user', 'app': 'models', 'pk_attr': 'id'},
            bases=['BaseModel', 'UUIDModel', 'TimestampMixin'],
        ),
        ops.CreateModel(
            name='Conversation',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('uuid', fields.UUIDField(default=uuid7, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(db_index=True, auto_now=True, auto_now_add=False)),
                ('title', fields.CharField(default='New chat', max_length=200)),
                ('model_str', fields.CharField(default='deepseek-chat', max_length=50)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='conversation', on_delete=OnDelete.CASCADE)),
            ],
            options={'table': 'conversation', 'app': 'models', 'pk_attr': 'id', 'table_description': '对话/会话'},
            bases=['BaseModel', 'UUIDModel', 'TimestampMixin'],
        ),
        ops.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('uuid', fields.UUIDField(default=uuid7, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(db_index=True, auto_now=True, auto_now_add=False)),
                ('role', fields.CharField(max_length=20)),
                ('content', fields.TextField(unique=False)),
                ('token_count', fields.IntField(null=True)),
                ('conversation', fields.ForeignKeyField('models.Conversation', source_field='conversation_id', db_constraint=True, to_field='id', related_name='message', on_delete=OnDelete.CASCADE)),
            ],
            options={'table': 'chat_message', 'app': 'models', 'pk_attr': 'id', 'table_description': '聊天消息'},
            bases=['BaseModel', 'UUIDModel', 'TimestampMixin'],
        ),
        ops.CreateModel(
            name='Note',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('uuid', fields.UUIDField(default=uuid7, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(db_index=True, auto_now=True, auto_now_add=False)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_index=True, db_constraint=True, to_field='id', related_name='notes', on_delete=OnDelete.CASCADE)),
                ('content', fields.TextField(default='', unique=False)),
                ('title', fields.CharField(default='Untitled', db_index=True, max_length=255)),
                ('preview', fields.CharField(default='', max_length=100)),
                ('deleted_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
            ],
            options={'table': 'note', 'app': 'models', 'indexes': [Index(fields=['user_id', 'deleted_at', 'updated_at'])], 'pk_attr': 'id'},
            bases=['BaseModel', 'UUIDModel', 'TimestampMixin'],
        ),
    ]
