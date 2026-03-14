# app/media/router.py
"""
Media 모듈 인바운드 라우터.

책임: HTTP 요청 수신 + 응답 반환만

- 변환:       MediaMapper 위임    (interface/mapper.py)
- 파이프라인: ProcessMediaUseCase  (application/use_case/)
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, status

from core.schema import ApiResponse

from media.application.service                       import MediaService
from media.application.usecase.process_media_usecase import ProcessMediaUseCase
from media.infrastructure.di                         import get_media_service
from media.infrastructure.di                         import get_process_media_usecase
from media.interface                                 import MediaMapper
from media.interface.schema import (
    ProcessMediaRequest,
    GazeSegmentRequest,
    AcceptedData,
)

logger    = logging.getLogger(__name__)
router    = APIRouter(prefix="/internal/v1", tags=["media"])
_mapper   = MediaMapper()
_use_case = ProcessMediaUseCase()


@router.post(
    # "/process",
    "/answers/analyze",
    status_code = status.HTTP_202_ACCEPTED,
    response_model = ApiResponse[AcceptedData],
    summary = "미디어 파이프라인 처리 요청",
)
async def process_media(
    request:          ProcessMediaRequest,
    background_tasks: BackgroundTasks,
    usecase         : ProcessMediaUseCase = Depends(get_process_media_usecase)
) -> ApiResponse[AcceptedData]:

    command = _mapper.to_process_command(request)
    background_tasks.add_task(usecase.execute, command)

    logger.info(
        "파이프라인 요청 수락 interview_id=%s question_id=%s",
        request.interview_id, request.question_id,
    )

    return ApiResponse[AcceptedData](
        success = True,
        code = "MEDIA_ACCEPTED",
        message = "파이프라인 처리가 시작되었습니다.",
        data = AcceptedData(
            interview_id = request.interview_id,
            question_id = request.question_id,
        ),
    )

@router.post(
    # "/gaze/segment",
    "/gaze-batches",
    status_code = status.HTTP_204_NO_CONTENT,
    summary="Gaze 세그먼트 버퍼 적재",
)
async def buffer_gaze_segment(
    request: GazeSegmentRequest,
    service: MediaService = Depends(get_media_service),
) -> None:

    segment = _mapper.to_gaze_segment(request)
    await service.buffer_gaze_segment(segment)

    logger.debug(
        "Gaze 세그먼트 적재 interview_id=%s question_id=%s seq=%d",
        request.meta.interview_id,
        request.meta.question_id,
        request.meta.segment_sequence,
    )