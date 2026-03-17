from __future__ import annotations

from abc import ABC, abstractmethod

from app.media.domain.pipeline.media_processing_result import MediaProcessingResult


class MediaEventPort(ABC):
    """
    파이프라인 완료 내부 이벤트 발행 아웃바운드 포트.
    """
    
    @abstractmethod
    def publish_completed(self, result: MediaProcessingResult) -> None:
        """
        파이프라인 완료 이벤트 발행
        feedback 도메인 수신
        non-blocking

        Args:
            result: 파이프라인 처리 결과
        """
        ...