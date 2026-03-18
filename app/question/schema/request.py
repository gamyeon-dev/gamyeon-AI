from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FileEntry(BaseModel):
    fileType: Literal["RESUME", "PORTFOLIO", "SELF_INTRODUCTION"]
    fileKey: str


class QuestionGenerateRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    intvId: int
    files: list[FileEntry]
    # ↓ 아래 필드 전부 삭제 (files[]로 통합되었음)
    # resume_url: str               ← 삭제
    # portfolio_url: str | None     ← 삭제
    # self_introduction_url: str | None ← 삭제
    # job_role: str | None          ← 삭제

    def get_file_key(self, file_type: str) -> str | None:
        for f in self.files:
            if f.fileType == file_type:
                return f.fileKey
        return None
