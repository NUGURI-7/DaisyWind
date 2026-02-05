from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    INSERT INTO `user` (`uuid`,`username`,`email`,`password`,`is_admin`)
    VALUES (
        '019c1efb-868c-75d3-af00-c4b65057786a',
        'admin',
        'nuguri990717@gmail.com',
        '$2b$12$3sN32/WpKEoCHCRMIItQ.uLx0WwLZrCvzZfpX0NBsuNUM63wSiKES',
        1
    );
    """


async def downgrade(db: BaseDBAsyncClient):
    await  "DELETE FROM `user` WHERE username='admin'"


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
