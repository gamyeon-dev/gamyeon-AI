import logging
from pathlib import Path

from app.question.application.port.s3_download_port import S3DownloadPort

logger = logging.getLogger(__name__)


class LocalFileAdapter(S3DownloadPort):
    TEST_DATA_DIR = Path("./test")

    async def download(self, file_key: str) -> bytes:
        try:
            local_path = self.TEST_DATA_DIR / file_key

            logger.info(f"로컬 파일: {local_path}")
            if not local_path.exists():
                raise FileNotFoundError(f"테스트 파일 없음: {local_path}")

            with open(local_path, "rb") as f:
                data = f.read()
                logger.info(f"로컬 완료: {len(data)} bytes")
                return data

        except FileNotFoundError as e:
            logger.error(f"파일 없음: {e}")
            raise ValueError(f"테스트 파일 준비: {local_path}") from e
        except Exception as e:
            logger.error(f"로컬 실패: {e}")
            raise Exception(f"로컬 처리 실패: {e}") from e
