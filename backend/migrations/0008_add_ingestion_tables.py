from tortoise import migrations
from tortoise.migrations import operations as ops
from orjson import loads
from tortoise.fields.base import OnDelete
from tortoise.fields.data import JSON_DUMPS
from uuid_utils.compat import uuid7
from tortoise import fields
from tortoise.indexes import Index

class AlterFieldStateOnly(ops.AlterField):
    """仅更新状态，不动 DB。前进、后退都为 no-op。"""
    async def database_forward(self, app_label, old_state, new_state, state_editor=None):
        return

    async def database_backward(self, app_label, old_state, new_state, state_editor=None):
        return

class Migration(migrations.Migration):
    dependencies = [('models', '0007_drop_redundant_unique_indexes')]

    initial = False

    operations = [
        ops.CreateModel(
            name='WorkflowTemplate',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('workflow_key', fields.CharField(description='业务标识，多版本共享', max_length=64)),
                ('version', fields.IntField(description='单调递增版本号')),
                ('parent_version', fields.IntField(null=True, description='上一版本号，首版为 null')),
                ('definition', fields.JSONField(description='图定义，启动时从 YAML 解析后写入', encoder=JSON_DUMPS, decoder=loads)),
                ('source_path', fields.CharField(description='YAML 文件路径，追溯用', max_length=255)),
                ('is_system', fields.BooleanField(default=True, description='系统内置；用户编辑场景写 false')),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'workflow_template', 'app': 'models', 'unique_together': (('workflow_key', 'version'),), 'pk_attr': 'id', 'table_description': '工作流定义模板。'},
            bases=['BaseModel'],
        ),
        ops.CreateModel(
            name='IngestionRun',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('uuid', fields.UUIDField(default=uuid7, unique=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='ingestion_runs', on_delete=OnDelete.CASCADE)),
                ('template', fields.ForeignKeyField('models.WorkflowTemplate', source_field='template_id', null=True, description='仅追踪来源，模板被删不影响已跑的 run', db_constraint=True, to_field='id', related_name='runs', on_delete=OnDelete.SET_NULL)),
                ('source_type', fields.CharField(description='deepseek_share | internal | pasted | ...', max_length=32)),
                ('source_ref', fields.CharField(description='输入源标识（URL / conversation_id / hash 占位等）', max_length=512)),
                ('graph_snapshot', fields.JSONField(description='启动时从 template.definition 复制的副本', encoder=JSON_DUMPS, decoder=loads)),
                ('graph_schema_version', fields.IntField(default=1, description='snapshot schema 版本')),
                ('status', fields.CharField(default='pending', description='pending|running|awaiting_user|cancelling|cancelled|succeeded|failed', max_length=20)),
                ('blackboard', fields.JSONField(default=dict, description='运行时状态 + 节点状态 + 节点输出', encoder=JSON_DUMPS, decoder=loads)),
                ('budget_tokens', fields.IntField(null=True, description='token 预算上限，null = 无限制')),
                ('budget_cost_usd', fields.DecimalField(null=True, description='成本预算上限（USD）', max_digits=10, decimal_places=6)),
                ('awaiting_since', fields.DatetimeField(null=True, description='进入 awaiting_user 的时间', auto_now=False, auto_now_add=False)),
                ('locked_by', fields.CharField(null=True, description='worker 持锁标识', max_length=128)),
                ('locked_until', fields.DatetimeField(null=True, description='锁过期时间', auto_now=False, auto_now_add=False)),
                ('completed_at', fields.DatetimeField(null=True, description='完成/失败/取消的时刻', auto_now=False, auto_now_add=False)),
            ],
            options={'table': 'ingestion_run', 'app': 'models', 'indexes': [Index(fields=['user_id', 'created_at'])], 'pk_attr': 'id', 'table_description': 'Ingestion 一次执行的实例。'},
            bases=['BaseModel', 'UUIDModel', 'TimestampMixin'],
        ),
        ops.CreateModel(
            name='IngestionEvent',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('run', fields.ForeignKeyField('models.IngestionRun', source_field='run_id', description='所属 run，run 删除时事件一并清除', db_constraint=True, to_field='id', related_name='events', on_delete=OnDelete.CASCADE)),
                ('seq', fields.IntField(description='每个 run 内单调递增序号，断点重放用')),
                ('ts', fields.DatetimeField(description='事件发生时刻', auto_now=False, auto_now_add=True)),
                ('actor', fields.CharField(description='事件发起者：engine | <node_id> | user | system', max_length=64)),
                ('kind', fields.CharField(description='事件类型：node_started / node_completed / await_user / run_completed 等', max_length=32)),
                ('payload', fields.JSONField(default=dict, description='事件载荷', encoder=JSON_DUMPS, decoder=loads)),
            ],
            options={'table': 'ingestion_event', 'app': 'models', 'unique_together': (('run_id', 'seq'),), 'pk_attr': 'id', 'table_description': 'Ingestion 执行过程中的事件流，append-only，用于 SSE 推送和断点重放。'},
            bases=['BaseModel'],
        ),
        AlterFieldStateOnly(
            model_name='ChatMessage',
            name='content',
            field=fields.JSONField(encoder=JSON_DUMPS, decoder=loads),
        ),
    ]
