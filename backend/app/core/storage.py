"""
    @project: DaisyWind
    @Author: niu
    @file: storage.py
    @date: 2026/3/13 23:31
    @desc:
"""

import boto3
from botocore.config import Config

from config import settings


class R2Storage:

    def __init__(self):
        # 初始化 boto3 客户端连接 R2
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",  # R2 固定使用 auto
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.R2_BUCKET_NAME

    def generate_pre_signed_upload_url(self, object_name: str, content_type: str = "application/octet-stream",
                                       expiration: int = 300) -> dict:
        """
        生成预签名上传 URL，前端可以用 PUT 方法直接把文件传到这个 URL
        """
        # 生成上传用的直传 URL
        pre_signed_url = self.s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_name,
                "ContentType": content_type  # 泛指任意二进制流
            },
            ExpiresIn=expiration,
        )
        # 生成将来访问这张图片的公共 URL
        # 如果配了绑定的域名就用域名，没配的话前端先不能直接预览，等你绑好域名补上 R2_PUBLIC_URL 就能看了
        public_url = f"{settings.R2_PUBLIC_URL}/{object_name}" if settings.R2_PUBLIC_URL else ""

        return {
            "upload_url": pre_signed_url,
            "public_url": public_url
        }

    def upload_bytes(
            self,
            data: bytes,
            object_name: str,
            content_type: str = 'application/octet-stream'
    ) -> str:
        """
                后端直传：把二进制数据上传到 R2，返回公网可访问的 URL。

                用于后端生成的内容（如 AI 生成图片），区别于前端直传的预签名方式。
                调用方应使用 asyncio.to_thread 包装此方法以避免阻塞事件循环。
                """
        if not settings.R2_PUBLIC_URL:
            raise ValueError("R2_PUBLIC_URL is not configured; cannot build public URL.")

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=object_name,
            Body=data,
            ContentType=content_type,
        )

        return f"{settings.R2_PUBLIC_URL}/{object_name}"

r2_storage = R2Storage()
