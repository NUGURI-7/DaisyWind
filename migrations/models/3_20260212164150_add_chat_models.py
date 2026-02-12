from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `conversation` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `uuid` CHAR(36) NOT NULL UNIQUE,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `title` VARCHAR(200) NOT NULL DEFAULT 'New chat',
    `model_str` VARCHAR(50) NOT NULL DEFAULT 'deepseek-chat',
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_conversa_user_84883661` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    KEY `idx_conversatio_uuid_343261` (`uuid`),
    KEY `idx_conversatio_created_7f8ebc` (`created_at`),
    KEY `idx_conversatio_updated_1abcf7` (`updated_at`)
) CHARACTER SET utf8mb4 COMMENT='对话/会话';
        CREATE TABLE IF NOT EXISTS `chat_message` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `uuid` CHAR(36) NOT NULL UNIQUE,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `role` VARCHAR(20) NOT NULL,
    `content` LONGTEXT NOT NULL,
    `token_count` INT,
    `conversation_id` BIGINT NOT NULL,
    CONSTRAINT `fk_chat_mes_conversa_3427e5d0` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`id`) ON DELETE CASCADE,
    KEY `idx_chat_messag_uuid_28d2cb` (`uuid`),
    KEY `idx_chat_messag_created_ada9bd` (`created_at`),
    KEY `idx_chat_messag_updated_7475c3` (`updated_at`)
) CHARACTER SET utf8mb4 COMMENT='聊天消息';
        CREATE TABLE IF NOT EXISTS `basemodel` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `basemodel`;
        DROP TABLE IF EXISTS `chat_message`;
        DROP TABLE IF EXISTS `conversation`;"""


MODELS_STATE = (
    "eJztmm1v4jgQx78Kyqut1O1BIEBPp5OgpbvcFji19G61yyoyiaEWicMmztFq1e9+tsmj81"
    "BCgZYqb6ownknt30xi/+38kkxLh4ZzdnEPyAA6DphD6ffKLwkDk12kNZ9WJLBcho3MQMDU"
    "4P4adVTNiOfUITbQCG2bAcOB1KRDR7PRkiALs4iJ2642wMRVzuXzidvU2236t9qcsWjd0m"
    "g4wvPnHF2MfrpQJdYckntoU/fvP6gZYR0+QMf/uVyoMwQNPTZCpLMbcLtKHpfc1kXzPiZX"
    "3Jd1Y6pqluGaOPRfPpJ7CwcBCBNmnUMMbUAg+w/EdtlosWsYHhwfwLqzocu6l5EYHc6Aaz"
    "BmLDqBzDdG4HgmzcIMN+2Nw8fIk/nxXJbr9ZZcrTfbSqPVUtrVNvXlXUo2tZ7WAw6BrG/F"
    "sfQ/9YdjNlCL5nSdcGZ44jGAgHUU5x0Cdt00xHd3/ct0wL6/gJiZz1iUCNrH+jLS0h8zF2"
    "uMcIX9J9UliNa9ZplLQM6YpfWntH0mcqBefO7cfKg3T/iQLYfMbd7IAXGyIUnNhmzMKiBJ"
    "npe0hSATpjONRwpkdS/0zL/YhrBv2F8x0yHoI2w8erfOQTruD3q3487gbzYQ03F+GpxQZ9"
    "xjLTK3PgrWD+sMhIUd3KTyb3/8ucJ+Vr6Nhj0xT4Hf+JvE+gRcYqnYWqlAj1DwrT6pWF7d"
    "pb5lXuORZV5fM69e58O02pYBkwmlU6mdnkzfX0gjhbWbxIUT8I4yZ4IH1YB4Tu7pT7mak7"
    "l/Ojf8PSdXT8R3moUJxCmFP4YPGTNwJORYUOUVde/rOFbPQx/WoPP1JFbT16PhJ989LOjh"
    "xfWoK1Al1gJiisxNI5u5tBGinl/jpMD1notDluF6lSPXGq1Gu95sBIubwJK3pvHXL7GK/A"
    "/aDmD9UIuuDlOCt8L4Go/zwVaLbC0+W6QuFqP8kuSvLBuiOf4CHzn9Pu0/wFraS9PXLcLt"
    "3h71J7+CfGv4DNlgFeiVtMKiF3SQkKynlc7tReeyJ3G4U6AtVsDW1Rhl1mLJlmAJfJNNpm"
    "yKFoCpsNO90bC+p4FOE5BCInIUpOi5gYJUpjMqCdtTXf9t4jZmNbD+kSIhczxLDVlqyFJD"
    "lhryGLRGqSHfZ14TGpIgUkxEBgGHk0bSEK4qbOP3BS83UUtuJiYTapKvJ1RvrJsiiwUdEJ"
    "sO4dKBcPFxp+yUTdApCXKuA+3CaicSVKqcAiqHcduBurnzbvP2KG+qaiIFVFTNRB768LhJ"
    "KF0v8OrLDTQCQZGhFOMnXMeD9Gmfso5XWIqc8ysvW8b5Jf6sfMsGUAqyUpCVgqwUZMewcC"
    "8F2fvMa0KQsXmNXyeSmi0wojG70RdbTjLSxG0pMvtuRq63Jq7SqOrUcj6rijulezzww0hb"
    "qEUJxoIOKNGSswNF2GzWle2xbanPbIAXauHdgHjUa4NjyGjV1WetA4KDJkBGEWZBwGs/qu"
    "dVACm06bS21eOpKJs8n4oiAlsCx1lZdsryLptZNGYrbDs7NuZnPFqTcmtXt+JWk9sbcKNe"
    "Ijfk0FnERCnHll3LMiDAGdIjEiagm9K4PU3vGUdpQU9etPrtjkbXsdm82xe/WbgbdHuUIp"
    "/GqRMieRsnm2wC5B8cF9oJONoz471uBXSBAwfsUkrZDwgbT/M2BabUzQzcyp2B97MzUOCZ"
    "3WeRdqCNtPu0CvVacssThD5vpjbfUWG+8Aut7M0o9rpOfe1nL1giIcfyDeGOlnes/AuA8t"
    "yPE1Jto3PEWvIcMfOr1L9uR8OiX6XeYTqI7zrSyGnFQA758TbR5ZBio44t6BLfqIqfo57G"
    "913YDbrFlna7nyae/gdZyfVB"
)
