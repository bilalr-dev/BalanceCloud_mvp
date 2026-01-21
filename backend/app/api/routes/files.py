"""
Simplified File Management Routes for MVP
"""

import io
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.file import FileCreate, FileListResponse, FileResponse
from app.services.encryption_service import encryption_service
from app.services.file_service import file_service

router = APIRouter()


# Simple in-memory user key storage for MVP (in production, store encrypted in DB)
_user_keys: dict[str, bytes] = {}


def _get_user_key(user_id: str) -> bytes:
    """Get or create user encryption key"""
    if user_id not in _user_keys:
        _user_keys[user_id] = encryption_service.generate_user_key()
    return _user_keys[user_id]


@router.get("", response_model=FileListResponse)
async def list_files(
    parent_id: Optional[str] = Query(None, description="Parent folder ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List files in a folder"""
    try:
        files = await file_service.list_files(db, str(current_user.id), parent_id)
        return FileListResponse(
            files=[FileResponse.model_validate(file) for file in files],
            total=len(files),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}",
        )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get file metadata by ID"""
    file = await file_service.get_file(db, str(current_user.id), file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return FileResponse.model_validate(file)


@router.post(
    "/folders", response_model=FileResponse, status_code=status.HTTP_201_CREATED
)
async def create_folder(
    request: FileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new folder"""
    try:
        folder = await file_service.create_folder(
            db=db,
            user_id=str(current_user.id),
            name=request.name,
            parent_id=request.parent_id,
        )
        return FileResponse.model_validate(folder)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    parent_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file with chunked encryption
    
    Pipeline:
    1. Receive file upload
    2. Save to staging area
    3. Chunk and encrypt
    4. Move to final storage
    5. Store metadata
    """
    try:
        # Read file data
        file_data = await file.read()

        # Get user encryption key (aligned with contract)
        user_key = await _get_user_key(str(current_user.id), db)

        # Save encrypted file (uses staging area internally)
        saved_file = await file_service.save_file(
            db=db,
            user_id=str(current_user.id),
            name=file.filename or "untitled",
            file_data=file_data,
            mime_type=file.content_type,
            parent_id=parent_id,
            user_key=user_key,
        )
        return FileResponse.model_validate(saved_file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a file"""
    try:
        # Get user encryption key (aligned with contract)
        user_key = await _get_user_key(str(current_user.id), db)

        # Get and decrypt file data
        file_data = await file_service.get_file_data(
            db, str(current_user.id), file_id, user_key
        )

        # Get file metadata
        file = await file_service.get_file(db, str(current_user.id), file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=file.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{file.name}"',
                "Content-Length": str(len(file_data)),
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}",
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a file or folder"""
    try:
        success = await file_service.delete_file(db, str(current_user.id), file_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )
