from __future__ import annotations

from abc import ABC, abstractmethod

from media.domain.pipeline.media_processing_result import MediaProcessingResult

class ResultWebhookPort(ABC):
    """
    파이프라인 결과 Spring Boot 전송 아웃바운드 포트.
    """

    @abstractmethod
    async def send_success(self, result: MediaProcessingResult) -> None:
        """
        처리 완료 결과 전송 (DONE)

        Args:
            result: 파이프라인 처리 결과
        """
        ...

    @abstractmethod
    async def send_failed(
        self,
        interview_id: int,
        question_id:  int,
        error_code:   str,
        message:      str,
    ) -> None:
        """
        처리 실패 결과 전송 (FAILED)

        Args:
            interview_id: 면접 세션 ID
            question_id:  질문 ID
            error_code:   실패 코드
            message:      실패 메시지
        """
        ...