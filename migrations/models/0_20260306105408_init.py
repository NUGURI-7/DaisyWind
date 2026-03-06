from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "nick_name" VARCHAR(50) NOT NULL  DEFAULT '',
    "rank_title" VARCHAR(50) NOT NULL  DEFAULT '',
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(128),
    "is_admin" BOOL NOT NULL  DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_user_uuid_863a0b" ON "user" ("uuid");
CREATE INDEX IF NOT EXISTS "idx_user_created_b19d59" ON "user" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_user_updated_dfdb43" ON "user" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_user_usernam_9987ab" ON "user" ("username");
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
CREATE INDEX IF NOT EXISTS "idx_user_is_admi_2da030" ON "user" ("is_admin");
COMMENT ON COLUMN "user"."username" IS '用户名称';
COMMENT ON COLUMN "user"."nick_name" IS '昵称';
COMMENT ON COLUMN "user"."rank_title" IS '称号';
COMMENT ON COLUMN "user"."email" IS '邮箱';
COMMENT ON COLUMN "user"."password" IS '密码';
COMMENT ON COLUMN "user"."is_admin" IS 'admin';
CREATE TABLE IF NOT EXISTS "conversation" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(200) NOT NULL  DEFAULT 'New chat',
    "model_str" VARCHAR(50) NOT NULL  DEFAULT 'deepseek-chat',
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_conversatio_uuid_343261" ON "conversation" ("uuid");
CREATE INDEX IF NOT EXISTS "idx_conversatio_created_7f8ebc" ON "conversation" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_conversatio_updated_1abcf7" ON "conversation" ("updated_at");
COMMENT ON TABLE "conversation" IS '对话/会话';
CREATE TABLE IF NOT EXISTS "chat_message" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "uuid" UUID NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "role" VARCHAR(20) NOT NULL,
    "content" TEXT NOT NULL,
    "token_count" INT,
    "conversation_id" BIGINT NOT NULL REFERENCES "conversation" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_chat_messag_uuid_28d2cb" ON "chat_message" ("uuid");
CREATE INDEX IF NOT EXISTS "idx_chat_messag_created_ada9bd" ON "chat_message" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_chat_messag_updated_7475c3" ON "chat_message" ("updated_at");
COMMENT ON TABLE "chat_message" IS '聊天消息';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmmtv4jgUhv8Kyqep1OlCIFxWq5WgpTPsFFi1dHc0wygyiaEWicMkzrbViP++tsnVuZ"
    "RQSkuVLxUcn5PazznGfu38kkxLh4Zzdn4HyBA6DlhA6ffKLwkDk31Iaz6tSGC1ChuZgYCZ"
    "wf016qiaEc+ZQ2ygEdo2B4YDqUmHjmajFUEWZhFTt11tgKmrdOTO1G3q7Tb9W23OWbRuaT"
    "Qc4cVTji5GP12oEmsByR20qfv3H9SMsA4foON/XS3VOYKGHhsh0tkDuF0ljytu66HFAJNL"
    "7su6MVM1y3BNHPqvHsmdhYMAhAmzLiCGNiCQ/Qdiu2y02DUMD44PYNPZ0GXTy0iMDufANR"
    "gzFp1A5hsjcDyTZmGGm/bG4WPkyfzYkeV6vSVX68220mi1lHa1TX15l5JNrfVmwCGQzaM4"
    "lsGnwWjCBmrRnG4SzgxrHgMI2ERx3iFg101DfHs7uEgH7PsLiJn5jEWJoH2szyMt/TF3sc"
    "YIV9h/Ul2CaN1rlrkC5IxZWn9Ku2ciB+r55+71h3rzhA/ZcsjC5o0cECcbktRsyMasApLk"
    "eUFbCDJhOtN4pEBW90LP/A+7EPYNL1fMdAj6GBuP3qNzkE4Gw/7NpDv8mw3EdJyfBifUnf"
    "RZi8ytj4L1wyYDYWEHD6n8O5h8rrCvlW/jUV/MU+A3+SaxPgGXWCq27lWgRyj4Vp9ULK/u"
    "St8xr/HIMq+vmVev82FabcuAyYTSpdROT6bvL6SRwtpP4sIFeE+ZM8GDakC8IHf0q1zNyd"
    "w/3Wv+OydXT8TfNAsTiFMKfwIfMlbgSMixoMor6v7XSayeRz6sYffrSaymr8ajT757WNCj"
    "86txT6BKrCXEFJmbRjZzayNEPb3HSYHrzYtDluFmlyPXGq1Gu95sBJubwJK3p/H3L7GK/A"
    "/aDmD9UIvuDlOCd8L4GtP5YLtFthefL1M3i1F+SfKXlg3RAn+Bj5z+gPYfYC3tR9PXLcLj"
    "3h71tV9BvjWcQza4D/RKWmHRD3SQkGyWle7NefeiL3G4M6At74GtqzHKrMWSLcES+CabTN"
    "kULQBTYad7o2F9TwOdJiCFROQoSNFzCwWpzOZUErZnuv7b1G3Ma2DzJUVC5niWGrLUkKWG"
    "LDXkMWiNUkO+z7wmNCRBpJiIDAIOJ42kEbyvsIPfZ/y4iVpyOzGZUJN8P6F6Y90WWSzogN"
    "h0CFcOhMuPe2WnbINOSZBzHWgXVjuRoFLlFFA5jNse1M2t95i3R3lbVRMpoKJqJjLpw+sm"
    "oXS9wMsv19AIBEWGUozfcB0P0vVLyjpeYSlyzq+8bBnnl/iT8i0bQCnISkFWCrJSkB3Dxr"
    "0UZO8zrwlBxtY1/jmR1GyBEY3Zj77YcZGRpm5Lkdl7M3K9NXWVRlWnls68Kp6UvuCFH0ba"
    "Ui1KMBZ0QImWXB0owmazruyObUd9ZgO8VAufBsSjXhscQ0arrj5vHRAcNAEyijALAl57qn"
    "aqAFJos1ltp+mpKNvMT0URga2A49xbdsr2LptZNGYnbHu7NuZ3PFqTcmtXd+JWk9tbcKNe"
    "Ijfk0FXERCnXlj3LMiDAGdIjEiagm9G4F1reM67Sgp48a/fbG4+vYqt5byC+s3A77PUpRb"
    "6MUydE8g5OtjkEyL84LnQScLR3xi96FNCFNtLupJTDAK/lNO84AIQ+b+ZA4B2dBjzz5Zds"
    "nc9mQuqMyl4LIiHH8nrWnlZOVv4FQHnuxwmpttUVTS15RZP5wt9fN+NR0Rf+bjEdxHcdae"
    "S0YiCH/Hib6HJIsVHH1srE63/im36ncUnLHtArtmruf5lY/w+EZyBP"
)
