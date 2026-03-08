from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "note" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "content" TEXT NOT NULL,
    "title" VARCHAR(255) NOT NULL DEFAULT 'Untitled',
    "preview" VARCHAR(100) NOT NULL DEFAULT '',
    "deleted_at" TIMESTAMPTZ,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_note_uuid_68a667" ON "note" ("uuid");
CREATE INDEX IF NOT EXISTS "idx_note_created_faed43" ON "note" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_note_updated_b64cfc" ON "note" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_note_title_c23a5d" ON "note" ("title");
CREATE INDEX IF NOT EXISTS "idx_note_user_id_25080a" ON "note" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_note_user_id_7c665e" ON "note" ("user_id", "deleted_at", "updated_at");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "note";"""


MODELS_STATE = (
    "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"
    "C3Sy5Q3FLxOv/wP0g3/o"
)
