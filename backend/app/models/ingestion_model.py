from tortoise import fields, models

from backend.app.db.base import BaseModel, UUIDModel, TimestampMixin


class WorkflowTemplate(BaseModel):
    """
        工作流定义模板。
        对应架构文档中的 Config-as-Code (YAML) 在数据库中的快照。
        采用不可变设计：一旦写入，代码逻辑禁止 Update，只允许 Insert 新版本。
    """
    workflow_key = fields.CharField(max_length=64, description="业务标识，多版本共享")
    version = fields.IntField(description="单调递增版本号")
    parent_version = fields.IntField(null=True, description="上一版本号，首版为 null")
    definition = fields.JSONField(description="图定义，启动时从 YAML 解析后写入")
    source_path = fields.CharField(max_length=255, description="YAML 文件路径，追溯用")
    is_system = fields.BooleanField(default=True, description="系统内置；用户编辑场景写 false")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "workflow_template"
        unique_together = ("workflow_key", "version")

    def __str__(self):
        return f"WorkflowTemplate(key={self.workflow_key} v={self.version})"


class IngestionRun(BaseModel, UUIDModel, TimestampMixin):
    """Ingestion 一次执行的实例。"""
    user = fields.ForeignKeyField(
        "models.User",
        related_name="ingestion_runs",
        on_delete=fields.CASCADE,
    )
    template = fields.ForeignKeyField(
        "models.WorkflowTemplate",
        related_name="runs",
        null=True,
        on_delete=fields.SET_NULL,
        description="仅追踪来源，模板被删不影响已跑的 run",
    )
    source_type = fields.CharField(
        max_length=32,
        description="deepseek_share | internal | pasted | ...",
    )
    source_ref = fields.CharField(
        max_length=512,
        description="输入源标识（URL / conversation_id / hash 占位等）",
    )
    graph_snapshot = fields.JSONField(description="启动时从 template.definition 复制的副本")
    graph_schema_version = fields.IntField(default=1, description="snapshot schema 版本")
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="pending|running|awaiting_user|cancelling|cancelled|succeeded|failed",
    )
    blackboard = fields.JSONField(default=dict, description="运行时状态 + 节点状态 + 节点输出")
    budget_tokens = fields.IntField(null=True, description="token 预算上限，null = 无限制")
    budget_cost_usd = fields.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        description="成本预算上限（USD）",
    )
    awaiting_since = fields.DatetimeField(null=True, description="进入 awaiting_user 的时间")
    locked_by = fields.CharField(max_length=128, null=True, description="worker 持锁标识")
    locked_until = fields.DatetimeField(null=True, description="锁过期时间")
    completed_at = fields.DatetimeField(null=True, description="完成/失败/取消的时刻")

    class Meta:
        table = "ingestion_run"
        ordering = ["-created_at"]
        indexes = [("user_id", "created_at")]

    def __str__(self):
        return f"IngestionRun(uuid={self.uuid} status={self.status})"


class IngestionEvent(BaseModel):
    """Ingestion 执行过程中的事件流，append-only，用于 SSE 推送和断点重放。"""
    run = fields.ForeignKeyField(
        "models.IngestionRun",
        related_name="events",
        on_delete=fields.CASCADE,
        description="所属 run，run 删除时事件一并清除",
    )
    seq = fields.IntField(description="每个 run 内单调递增序号，断点重放用")
    ts = fields.DatetimeField(auto_now_add=True, description="事件发生时刻")
    actor = fields.CharField(
        max_length=64,
        description="事件发起者：engine | <node_id> | user | system",
    )
    kind = fields.CharField(
        max_length=32,
        description="事件类型：node_started / node_completed / await_user / run_completed 等",
    )
    payload = fields.JSONField(default=dict, description="事件载荷")

    class Meta:
        table = "ingestion_event"
        unique_together = ("run_id", "seq")
        ordering = ["seq"]

    def __str__(self):
        return f"IngestionEvent(run={self.id} seq={self.seq} kind={self.kind})"