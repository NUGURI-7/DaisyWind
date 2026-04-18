from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [('models', '0004_rename_conversation_model')]

    initial = False

    operations = [
        ops.RunSQL(
            sql="""
            ALTER TABLE chat_message
              ALTER COLUMN content TYPE jsonb
              USING jsonb_build_array(
                jsonb_build_object('type', 'text', 'text', content)
              );
            """,
            reverse_sql="""
            ALTER TABLE chat_message
              ALTER COLUMN content TYPE text
              USING (content->0->>'text');
            """,
        ),
    ]