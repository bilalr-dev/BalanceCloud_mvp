"""
File Schemas - Simplified for MVP
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileBase(BaseModel):
    name: str
    path: str
    parent_id: Optional[str] = None


class FileCreate(FileBase):
    is_folder: bool = False


class FileResponse(BaseModel):
    id: str
    user_id: str
    name: str
    path: str
    size: int
    mime_type: Optional[str]
    is_folder: bool
    parent_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    files: list[FileResponse]
    total: int
