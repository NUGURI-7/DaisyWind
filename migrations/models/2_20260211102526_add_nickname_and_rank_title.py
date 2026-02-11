from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ADD `rank_title` VARCHAR(50) NOT NULL COMMENT '称号' DEFAULT '';
        ALTER TABLE `user` ADD `nick_name` VARCHAR(50) NOT NULL COMMENT '昵称' DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP COLUMN `rank_title`;
        ALTER TABLE `user` DROP COLUMN `nick_name`;"""


MODELS_STATE = (
    "eJztl21v2jAQx78KyqtV6lBICKHTNAlatjIVmFrYpj4oMokJFomdJs5aVPW7zzbkOTCgD3"
    "TT3iV/38V3v3NyuQfJJRZ0guoogL70ofIgYeBCdpHRDysS8LxE5QIFY0cYhpHFOKA+MCnT"
    "JsAJIJMsGJg+8igimKk4dBwuEpMZImwnUojRbQgNSmxIpyKOqxsmI2zBexhEt97MmCDoWJ"
    "kwkcX3FrpB557Q2sjuYvpZ2PINx4ZJnNDFib03p1OCYweEKVdtiKEPKOQ7UD/kGfAAl4lG"
    "SS2CTUwWUaZ8LDgBoUNTGW+IwSSYI2TRBCJHm+/y/khRVFVXZLXR1Oq6rjXlJrMVIRWX9M"
    "dFwgmQxaMElu6Xbn/IEyWsToviceFR+AAKFl6CdwI4DMsQj0bdk3LAkX0OMZer3CsPOsL6"
    "NNLSx0mITU64wncyQorY4TWJ6wFa5Yr+Sdq9EmugHp+2zt+pjQORMgmo7YtFAUiQTUiaPu"
    "Q5G4AWeZ6wFYpcWM4065kjay1dq9HFLoQj4eUOM0vBGmBnvnz0GqTDbq9zMWz1vvFE3CC4"
    "dQSh1rDDVxShznPqu0UFkoMdP6Tyozs8rfDbyuWg38nXKbYbXko8JhBSYmByZwArRSFSI1"
    "KZuoaetWNds57/67rPui6DT5WV9TVxXSjq8RT4Kwqa8smVk0F7mU9faf2k61DXlOZ12FBU"
    "/TrU6rLFlKOJLG1WVRfcGw7ENp2yW0VeU9XvrXPxDVTkg9z3DiNzZmxLMOP0PAiL70Dyfx"
    "L3j2J3YAgbDVXbHZu2CTatgM0HeGZQRJ2tuGW99g2OI2OnTp3orwgOugA52zCLHfb9qh7J"
    "ADJo43Ftp9dT0zZ5PzUtD8wDQXBH/JLfu9XM0j47YVtC2eqQreKmjc0G49aUd+JWU5obcG"
    "NWeW4oYF3ERbhk8iDEgQCvGD1Sbjl0Y+b3Qu29fBaT4kie9PfbHgzOMt283c0NGP1Rr91h"
    "FEUbZ0aIpuYOPtVNZqmxgwtjYM7ugG8ZhRWikFW2xSVXcfMKwMAWkHiePKvljNuCPjKnUs"
    "n0u1w5XDf/gsTmzUzA/9D4q9Tqer2pNurx1Bsr64bdPw+2v6Af8JC2+PilXF6vwz6R4vO0"
    "Cn78twC1NP87IdXkTf4/mFUeEnsqhbhkCvx6MeivmOwTlxysEWZJXFnIpIcVBwX05m2iW0"
    "OKZ51pDv2IXa/1MzfW9Y/PBu38DMcf0N53m3j8DRPzwXo="
)
