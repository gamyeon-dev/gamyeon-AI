import aioboto3
from app.question.application.port.s3_download_port import S3DownloadPort
from app.core.config import settings

class S3DownloadAdapter(S3DownloadPort):

    async def download(self, url: str) -> bytes:
        session = aioboto3.Session()
        async with session.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        ) as client:
            bucket, key = self._parse_url(url)
            response = await client.get_object(Bucket=bucket, Key=key)
            return await response["Body"].read()

    def _parse_url(self, url: str) -> tuple[str, str]:
        # s3://bucket-name/path/to/file.pdf
        path = url.replace("s3://", "")
        bucket, key = path.split("/", 1)
        return bucket, key
