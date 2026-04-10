from tortoise import migrations
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [('models', '0001_initial')]

    initial = False

    operations = [
        ops.RunSQL(
            sql="""
                INSERT INTO "user" (
                    "uuid", "username", "nick_name", "rank_title",
                    "email", "password", "is_admin",
                    "login_count", "last_login", "created_at", "updated_at"
                ) VALUES (
                    '019c1efb-868c-75d3-af00-c4b65057786a',
                    'admin', 'nuguri', 'VOYAGER',
                    'nuguri990717@gmail.com',
                    '$2b$12$3sN32/WpKEoCHCRMIItQ.uLx0WwLZrCvzZfpX0NBsuNUM63wSiKES',
                    true, 0, NULL, NOW(), NOW()
                ) ON CONFLICT ("email") DO NOTHING;
            """,
            reverse_sql="""DELETE FROM "user" WHERE "username" = 'admin';""",
        ),
    ]
