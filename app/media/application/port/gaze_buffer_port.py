from abc import ABC, abstractmethod

from app.media.domain import GazeSegment


class GazeBufferPort(ABC) :
    """
    Gaze 세그먼트 큐 추상화 포트.

    흐름:
    수신 시점 (답변 중):
        POST /internal/media/gaze/segment 수신
        → push() 호출
        → questionId 기준 버퍼에 segmentSequence 정렬 삽입

    처리 시점 (답변 종료):
        POST /internal/media/process 수신
        → pop_all() 호출
        → 정렬된 전체 세그먼트 반환 + 버퍼 제거
        → GazeAggregator.aggregate() 입력
    """

    @abstractmethod
    async def push(self, segment: GazeSegment) -> None :
        """
        세그먼트 버퍼 적재.

        Args:
            segment: 수신된 GazeSegment (raw_data[] 포함 전체)

        Note:
            segmentSequence 기준 정렬 삽입 보장.
            동일 questionId + segmentSequence 중복 수신 시
            마지막 수신 데이터로 덮어씀 (last-write-wins).
        """
        ...

    @abstractmethod
    async def pop_all(self, question_id: int) -> list[GazeSegment] :
        """
        questionId 기준 전체 세그먼트 반환 + 버퍼 제거.

        Args:
            question_id: 버퍼 키

        Returns:
            list[GazeSegment]: segmentSequence 오름차순 정렬 보장.
                버퍼 비어있으면 빈 리스트 반환.

        Note:
            호출 후 해당 questionId 버퍼 완전 제거.
            재호출 시 빈 리스트 반환.
        """
        ...

    @abstractmethod
    async def peek(self, question_id: int) -> list[GazeSegment] :
        """
        버퍼 상태 확인 (제거 없음).

        Args:
            question_id: 버퍼 키

        Returns:
            list[GazeSegment]: 현재 버퍼 내용 (정렬 완료).

        Note:
            디버깅 / 모니터링 전용.
            서비스 로직에서 호출 금지.
        """
        ...

    @abstractmethod
    async def clear(self, question_id: int) -> None :
        """
        버퍼 명시적 초기화.

        Args:
            question_id: 제거할 버퍼 키

        Note:
            파이프라인 FAILED 처리 시 잔여 세그먼트 정리 목적.
            pop_all() 없이 버퍼를 비워야 할 때 사용.
        """
        ...