from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0002_seed_admin')]

    initial = False

    operations = [
        ops.AddField(
            model_name='ChatMessage',
            name='cost',
            field=fields.DecimalField(null=True, max_digits=10, decimal_places=6),
        ),
        ops.AddField(
            model_name='Conversation',
            name='provider',
            field=fields.CharField(default='deepseek', max_length=20),
        ),
        ops.AddField(
            model_name='Conversation',
            name='summary',
            field=fields.TextField(null=True, unique=False),
        ),
    ]
