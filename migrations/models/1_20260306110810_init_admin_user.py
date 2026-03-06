from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "login_count" INT NOT NULL DEFAULT 0;
        ALTER TABLE "user" ADD "last_login" TIMESTAMPTZ;
        COMMENT ON COLUMN "user"."login_count" IS '登录次数';
        COMMENT ON COLUMN "user"."last_login" IS '最后登录时间';

        -- 如果此时还没有 admin，初始化一个管理员用户
        INSERT INTO "user" (
            "uuid",
            "username",
            "email",
            "password",
            "is_admin",
            "login_count",
            "last_login"
        )
        VALUES (
            '019c1efb-868c-75d3-af00-c4b65057786a',
            'admin',
            'nuguri990717@gmail.com',
            '$2b$12$3sN32/WpKEoCHCRMIItQ.uLx0WwLZrCvzZfpX0NBsuNUM63wSiKES',
            true,
            0,
            NULL
        )
        ON CONFLICT ("email") DO NOTHING;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "login_count";
        ALTER TABLE "user" DROP COLUMN "last_login";

        -- 降级时，如果需要可以删除内置 admin
        DELETE FROM "user" WHERE "username" = 'admin';
    """



MODELS_STATE = (
    "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"
    "dn+UuyXNVCHzCotmvufpt4/B+W8yRN"
)
