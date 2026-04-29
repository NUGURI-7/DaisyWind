from tortoise import migrations
from tortoise.migrations import operations as ops
from orjson import loads
from tortoise.fields.base import OnDelete
from tortoise.fields.data import JSON_DUMPS
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('models', '0005_chat_message_content_to_jsonb')]

    initial = False

    operations = [
        ops.AlterField(
            model_name='ChatMessage',
            name='created_at',
            field=fields.DatetimeField(auto_now=False, auto_now_add=True),
        ),
        ops.AlterField(
            model_name='ChatMessage',
            name='updated_at',
            field=fields.DatetimeField(auto_now=True, auto_now_add=False),
        ),
        ops.AddIndex(
            model_name='ChatMessage',
            index=Index(fields=['conversation_id', 'created_at']),
        ),
        ops.AlterField(
            model_name='Conversation',
            name='created_at',
            field=fields.DatetimeField(auto_now=False, auto_now_add=True),
        ),
        ops.AlterField(
            model_name='Conversation',
            name='updated_at',
            field=fields.DatetimeField(auto_now=True, auto_now_add=False),
        ),
        ops.AddIndex(
            model_name='Conversation',
            index=Index(fields=['user_id', 'updated_at']),
        ),
        ops.AlterField(
            model_name='Note',
            name='created_at',
            field=fields.DatetimeField(auto_now=False, auto_now_add=True),
        ),
        ops.AlterField(
            model_name='Note',
            name='title',
            field=fields.CharField(default='Untitled', max_length=255),
        ),
        ops.AlterField(
            model_name='Note',
            name='updated_at',
            field=fields.DatetimeField(auto_now=True, auto_now_add=False),
        ),
        ops.AlterField(
            model_name='Note',
            name='user',
            field=fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='notes', on_delete=OnDelete.CASCADE),
        ),
        ops.AlterField(
            model_name='User',
            name='created_at',
            field=fields.DatetimeField(auto_now=False, auto_now_add=True),
        ),
        ops.AlterField(
            model_name='User',
            name='is_admin',
            field=fields.BooleanField(default=False, description='admin'),
        ),
        ops.AlterField(
            model_name='User',
            name='updated_at',
            field=fields.DatetimeField(auto_now=True, auto_now_add=False),
        ),
    ]
