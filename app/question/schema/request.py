from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel



class FileEntry(BaseModel):
    fileType: Literal["RESUME", "PORTFOLIO", "SELF_INTRODUCTION"]
    fileKey:  str


class QuestionGenerateRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Spring이 보낸 camelCase를 받아들임
    )
    intvId: int
    files: list[FileEntry]
    callbackUrl: str
    resume_url: str
    portfolio_url: str | None = None
    self_introduction_url: str | None = None
    job_role: str

    def get_file_key(self, file_type: str) -> str | None:
        for f in self.files:
            if f.fileType == file_type:
                return f.fileKey
        return None
