from tortoise import migrations
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [('models', '0003_chat_about_model')]

    initial = False

    operations = [
        ops.RenameField(
            model_name='Conversation',
            old_name='model_str',
            new_name='model',
        ),
    ]
