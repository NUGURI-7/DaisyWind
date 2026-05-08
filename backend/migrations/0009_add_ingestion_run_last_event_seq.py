from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0008_add_ingestion_tables')]

    initial = False

    operations = [
        # 1. 先加 nullable 列
        ops.RunSQL(
            sql="ALTER TABLE ingestion_run ADD COLUMN last_event_seq INT;",
            reverse_sql="ALTER TABLE ingestion_run DROP COLUMN last_event_seq;",
        ),
        # 2. backfill 老数据
        ops.RunSQL(
            sql="""
            UPDATE ingestion_run
            SET last_event_seq = COALESCE(
                (SELECT MAX(seq) FROM ingestion_event WHERE run_id = ingestion_run.id),
                0
            );
            """,
            reverse_sql="-- no-op",
        ),
        # 3. 加 NOT NULL + default
        ops.RunSQL(
            sql="""
            ALTER TABLE ingestion_run
              ALTER COLUMN last_event_seq SET NOT NULL,
              ALTER COLUMN last_event_seq SET DEFAULT 0;
            """,
            reverse_sql="""
            ALTER TABLE ingestion_run
              ALTER COLUMN last_event_seq DROP NOT NULL,
              ALTER COLUMN last_event_seq DROP DEFAULT;
            """,
        ),
    ]
