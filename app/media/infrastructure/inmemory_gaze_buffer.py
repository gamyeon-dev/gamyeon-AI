"""
GazeBufferPort 구현체

dict 기반 인메모리 버퍼
questionId → segmentSequence 정렬 삽입 보장

MVP-2 교체 대상: RedisGazeBuffer (LPUSH/LRANGE 기반)
→ 장애 복구, 멀티 프로세스 공유, 재처리 가능

주의:
- 서버 재기동 시 버퍼 유실.
- 멀티 프로세스 환경에서 큐 공유 불가 → MVP-1 단일 프로세스 운영 기준으로 허용.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict

from media.application.port.gaze_buffer_port import GazeBufferPort
from media.domain import GazeSegment

logger = logging.getLogger(__name__)


class InMemoryGazeBuffer(GazeBufferPort):
    """
    인메모리 Gaze 세그먼트 버퍼

    _buffer: { question_id: [GazeSegment, ...] }
            segmentSequence 오름차순 정렬 유지
    _lock: 동일 questionId 동시 push 경합 방지
    """

    def __init__(self) -> None:
        self._buffer: dict[int, list[GazeSegment]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def push(self, segment: GazeSegment) -> None:
        """
        segmentSequence 기준 정렬 삽입
        중복 segmentSequence: last-write-wins (기존 항목 교체)
        """
        qid = segment.meta.question_id
        seq = segment.meta.segment_sequence

        async with self._lock:
            segments = self._buffer[qid]

            # 중복 제거 (last-write-wins)
            self._buffer[qid] = [
                s for s in segments
                if s.meta.segment_sequence != seq
            ]

            # 정렬 삽입
            self._buffer[qid].append(segment)
            self._buffer[qid].sort(
                key=lambda s: s.meta.segment_sequence
            )

        logger.debug(
            "Gaze 세그먼트 적재 question_id=%s seq=%d total=%d",
            qid, seq, len(self._buffer[qid]),
        )

    async def pop_all(self, question_id: int) -> list[GazeSegment]:
        """
        전체 반환 + 버퍼 제거
        segmentSequence 오름차순 보장
        """
        async with self._lock:
            segments = self._buffer.pop(question_id, [])

        logger.info(
            "Gaze 버퍼 pop_all question_id=%s count=%d",
            question_id, len(segments),
        )
        return segments

    async def peek(self, question_id: int) -> list[GazeSegment]:
        """버퍼 상태 확인 (제거 없음). 디버깅 전용."""
        async with self._lock:
            return list(self._buffer.get(question_id, []))

    async def clear(self, question_id: int) -> None:
        """버퍼 명시적 초기화. FAILED 처리 시 잔여 데이터 정리."""
        async with self._lock:
            removed = len(self._buffer.pop(question_id, []))

        logger.info(
            "Gaze 버퍼 초기화 question_id=%s removed=%d",
            question_id, removed,
        )