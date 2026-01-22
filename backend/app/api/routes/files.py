"""
Simplified File Management Routes for MVP
"""

import io
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
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
            files=[
                FileResponse(
                    id=str(file.id),
                    user_id=str(file.user_id),
                    name=file.name,
                    path=file.path,
                    size=file.size,
                    mime_type=file.mime_type,
                    is_folder=file.is_folder,
                    parent_id=str(file.parent_id) if file.parent_id else None,
                    created_at=file.created_at,
                    updated_at=file.updated_at,
                )
                for file in files
            ],
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
    return FileResponse(
        id=str(file.id),
        user_id=str(file.user_id),
        name=file.name,
        path=file.path,
        size=file.size,
        mime_type=file.mime_type,
        is_folder=file.is_folder,
        parent_id=str(file.parent_id) if file.parent_id else None,
        created_at=file.created_at,
        updated_at=file.updated_at,
    )


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
        return FileResponse(
            id=str(folder.id),
            user_id=str(folder.user_id),
            name=folder.name,
            path=folder.path,
            size=folder.size,
            mime_type=folder.mime_type,
            is_folder=folder.is_folder,
            parent_id=str(folder.parent_id) if folder.parent_id else None,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
        )
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
    background_tasks: BackgroundTasks = BackgroundTasks(),
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
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db, str(current_user.id)
        )

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
        
        # Automatically upload to cloud if user has a connected cloud account
        # This runs in background so the API response is fast
        async def upload_to_cloud():
            try:
                from app.services.cloud_upload_service import CloudUploadService, CloudProvider
                from app.core.database import AsyncSessionLocal
                
                # Create a new database session for background task
                async with AsyncSessionLocal() as db_session:
                    cloud_upload_service = CloudUploadService()
                    
                    # Check if user has a cloud account (prefer Google Drive, then OneDrive)
                    provider = await cloud_upload_service.select_provider(
                        db_session, str(current_user.id), preferred_provider=CloudProvider.GOOGLE_DRIVE
                    )
                    
                    if provider:
                        # Upload chunks to cloud
                        await cloud_upload_service.upload_file_chunks_to_cloud(
                            db=db_session,
                            user_id=str(current_user.id),
                            file_id=saved_file.id,
                            provider=provider,
                        )
            except Exception as e:
                # Log error but don't fail the upload if cloud upload fails
                import logging
                logging.error(f"Failed to upload file to cloud: {str(e)}")
        
        # Add background task for cloud upload
        background_tasks.add_task(upload_to_cloud)
        
        return FileResponse(
            id=str(saved_file.id),
            user_id=str(saved_file.user_id),
            name=saved_file.name,
            path=saved_file.path,
            size=saved_file.size,
            mime_type=saved_file.mime_type,
            is_folder=saved_file.is_folder,
            parent_id=str(saved_file.parent_id) if saved_file.parent_id else None,
            created_at=saved_file.created_at,
            updated_at=saved_file.updated_at,
        )
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
    """
    Download a file with streaming support
    
    Uses download_service for:
    - Chunk fetching from cloud or local storage
    - Decryption and reassembly
    - Streaming download
    - Checksum verification
    """
    try:
        # Get user encryption key (aligned with contract)
        user_key = await encryption_service.get_or_create_user_encryption_key(
            db, str(current_user.id)
        )

        # Get file metadata
        file = await file_service.get_file(db, str(current_user.id), file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        # Import download service (lazy import to avoid circular dependency)
        from app.services.download_service import download_service

        # Create async generator for streaming
        async def generate():
            async for chunk in download_service.stream_file_download(
                db, str(current_user.id), file_id, user_key
            ):
                yield chunk

        # Return as streaming response
        return StreamingResponse(
            generate(),
            media_type=file.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{file.name}"',
                # Note: Content-Length not set for streaming responses
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
