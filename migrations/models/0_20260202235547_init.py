from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `user` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `uuid` CHAR(36) NOT NULL UNIQUE,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名称',
    `email` VARCHAR(255) NOT NULL UNIQUE COMMENT '邮箱',
    `password` VARCHAR(128)   COMMENT '密码',
    `is_admin` BOOL NOT NULL  COMMENT 'admin' DEFAULT 0,
    KEY `idx_user_uuid_863a0b` (`uuid`),
    KEY `idx_user_created_b19d59` (`created_at`),
    KEY `idx_user_updated_dfdb43` (`updated_at`),
    KEY `idx_user_usernam_9987ab` (`username`),
    KEY `idx_user_email_1b4f1c` (`email`),
    KEY `idx_user_is_admi_2da030` (`is_admin`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztl21v2jAQx78KyqtW6qoQCKHTNAlatjIVmFrYpj4ochITrCZ2mthrUdXvPtskJJhAKW"
    "3Vbtq75O87++53iX2+10LiwSDZHyUw1j5W7jUMQsgfFvS9igaiKFeFQIETSEOWWTgJjYFL"
    "uTYGQQK55MHEjVFEEcFcxSwIhEhcboiwn0sMoxsGbUp8SCcyjosrLiPswTuYZK/RtT1GMP"
    "AWwkSeWFvqNp1GUmsjv4vpF2krFnRslwQsxLl9NKUTgucOCFOh+hDDGFAoVqAxExmIANNE"
    "s6RmweYmsygLPh4cAxbQQsYbYnAJFgh5NInM0RerfDgwjFrNMvRao2nWLcts6k1uK0NaHr"
    "IeZgnnQGZTSSzdr93+UCRKeJ1mxRPCg/QBFMy8JO8cMGNliEej7lE54MxeQSzkfeGlgs6w"
    "Po+09mnMsCsIV8RKNqOIf7wuCSNA94Vifda2r8QaqIfHrdOdWmNXpkwS6sdyUAKSZHOSbg"
    "xFzjagyzyP+AhFISxnuuipkPVS1/3sYRvCmfB6HzNPwRvgYJpOvQbpsNvrnA1bve8ikTBJ"
    "bgJJqDXsiBFDqlNF3ZlVIP+w55NUfnaHxxXxWjkf9DtqneZ2w3NNxAQYJTYmtzbwChQyNS"
    "O1UFcWeVvWddHzf13fsq5p8IWy8nNNPi8V9XAC4hUFLfgo5eTQXmfrK62fdsks02hesoZR"
    "sy6ZWdc9rhyMdW2zqobgzg4g9umEvxr6mqr+aJ3KPdDQd5X9DoYABU+hN3d4a3QHOoAcl+"
    "NUt8JlmpvwMk0VWASS5JbEJcftamZFn62wpVDW7Bh5N/cYN9NxG5xbU9+KW9VobsCNW6nc"
    "UML/6hDhkk6QkAACvKIVLLgp6Bzu90rbbXlvrM0jeVY30h4MThZ213ZXafj6o167wynKbZ"
    "UbIVroA0WXPb4utIFCcIB7fQtiz14aIQZZZbs8FBqhqgAMfAlJ5CmySu8cLRgjd6KV3EbS"
    "kb119xGQ27ybG8k/dB0xqnWr3qw16vNbyFxZd/l4/KLxG8aJCOkJm1/B5WWOjK03v80pvs"
    "xRIT7/J4BKzf9OSFV9k/6DW6mQ+KwU4pKu/NvZoL/ippW7KLBGmCdx4SGX7lUClNCr94lu"
    "DSmR9cLh0M/Y9Vq/lDa7f3gyaKs9tZig/dbHxMMfozX6Cg=="
)
