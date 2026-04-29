from tortoise import migrations
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [('models', '0006_history_model_change')]

    initial = False

    operations = [
        ops.RunSQL(
            sql="""
                DROP INDEX IF EXISTS "idx_user_email_1b4f1c";
                DROP INDEX IF EXISTS "idx_user_usernam_9987ab";
                DROP INDEX IF EXISTS "idx_user_uuid_863a0b";
                DROP INDEX IF EXISTS "idx_chat_messag_uuid_28d2cb";
                DROP INDEX IF EXISTS "idx_conversatio_uuid_343261";
                DROP INDEX IF EXISTS "idx_note_uuid_68a667";
                """,
            reverse_sql="""
                CREATE INDEX "idx_user_email_1b4f1c" ON "user" ("email");
                CREATE INDEX "idx_user_usernam_9987ab" ON "user" ("username");
                CREATE INDEX "idx_user_uuid_863a0b" ON "user" ("uuid");
                CREATE INDEX "idx_chat_messag_uuid_28d2cb" ON "chat_message" ("uuid");
                CREATE INDEX "idx_conversatio_uuid_343261" ON "conversation" ("uuid");
                CREATE INDEX "idx_note_uuid_68a667" ON "note" ("uuid");
                """,
        ),
    ]
