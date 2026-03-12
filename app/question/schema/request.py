from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class FileEntry(BaseModel):
    fileType: Literal["RESUME", "PORTFOLIO", "SELF_INTRODUCTION"]
    fileKey:  str


class QuestionGenerateRequest(BaseModel):
    intvId:      int
    files:       list[FileEntry]
    callbackUrl: str

    def get_file_key(self, file_type: str) -> str | None:
        for f in self.files:
            if f.fileType == file_type:
                return f.fileKey
        return None
