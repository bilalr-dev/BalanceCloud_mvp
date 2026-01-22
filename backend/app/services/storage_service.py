"""
Storage Service - Calculate and manage user storage usage
"""

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.models.user import User
from app.models.cloud_account import CloudAccount


class StorageService:
    """Service for calculating and managing user storage usage"""

    async def get_cloud_storage_usage(
        self, db: AsyncSession, user_id: str
    ) -> dict:
        """
        Get cloud storage usage for all connected cloud accounts
        
        Returns:
            {
                "google_drive": {
                    "used_bytes": 1024,
                    "total_bytes": 10737418240,
                    "used_percentage": 0.01,
                    "used_gb": 0.000001,
                    "total_gb": 10.0
                } or None,
                "onedrive": {
                    "used_bytes": 1024,
                    "total_bytes": 10737418240,
                    "used_percentage": 0.01,
                    "used_gb": 0.000001,
                    "total_gb": 10.0
                } or None
            }
        """
        from uuid import UUID
        from app.services.cloud_upload_service import CloudUploadService, CloudProvider
        from app.services.encryption_service import encryption_service
        
        cloud_usage = {
            "google_drive": None,
            "onedrive": None,
        }
        
        # Get all cloud accounts for user
        result = await db.execute(
            select(CloudAccount).where(CloudAccount.user_id == UUID(user_id))
        )
        accounts = result.scalars().all()
        
        if not accounts:
            # No cloud accounts found
            return cloud_usage
        
        cloud_upload_service = CloudUploadService()
        
        for account in accounts:
            try:
                # Get access token
                access_token = await cloud_upload_service.get_access_token(db, account)
                
                if account.provider == "google_drive":
                    # Get Google Drive storage quota
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            "https://www.googleapis.com/drive/v3/about",
                            headers={"Authorization": f"Bearer {access_token}"},
                            params={"fields": "storageQuota"},
                        )
                        if response.status_code == 200:
                            data = response.json()
                            quota = data.get("storageQuota", {})
                            
                            # Google Drive quota can be unlimited (null) or have limit/usage
                            limit_bytes = quota.get("limit")
                            usage_bytes = quota.get("usage", 0)
                            
                            if limit_bytes:
                                limit_bytes = int(limit_bytes)
                                usage_bytes = int(usage_bytes)
                                
                                used_percentage = (usage_bytes / limit_bytes * 100) if limit_bytes > 0 else 0
                                
                                cloud_usage["google_drive"] = {
                                    "used_bytes": usage_bytes,
                                    "total_bytes": limit_bytes,
                                    "used_percentage": round(used_percentage, 2),
                                    "used_gb": round(usage_bytes / (1024 ** 3), 2),
                                    "total_gb": round(limit_bytes / (1024 ** 3), 2),
                                }
                            else:
                                # Unlimited storage
                                cloud_usage["google_drive"] = {
                                    "used_bytes": usage_bytes,
                                    "total_bytes": None,  # Unlimited
                                    "used_percentage": 0,
                                    "used_gb": round(usage_bytes / (1024 ** 3), 2),
                                    "total_gb": None,  # Unlimited
                                }
                
                elif account.provider == "onedrive":
                    # Get OneDrive storage quota
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            "https://graph.microsoft.com/v1.0/me/drive/quota",
                            headers={"Authorization": f"Bearer {access_token}"},
                        )
                        if response.status_code == 200:
                            quota = response.json()
                            
                            total_bytes = quota.get("total")
                            used_bytes = quota.get("used", 0)
                            
                            if total_bytes:
                                total_bytes = int(total_bytes)
                                used_bytes = int(used_bytes)
                                
                                used_percentage = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
                                
                                cloud_usage["onedrive"] = {
                                    "used_bytes": used_bytes,
                                    "total_bytes": total_bytes,
                                    "used_percentage": round(used_percentage, 2),
                                    "used_gb": round(used_bytes / (1024 ** 3), 2),
                                    "total_gb": round(total_bytes / (1024 ** 3), 2),
                                }
                        else:
                            # Log API error
                            import logging
                            logging.warning(
                                f"OneDrive API error: {response.status_code} - {response.text}"
                            )
            except Exception as e:
                # Log error but don't fail the entire request
                import logging
                import traceback
                logging.warning(
                    f"Failed to get cloud storage usage for {account.provider} account {account.id}: {str(e)}"
                )
                logging.debug(traceback.format_exc())
        
        return cloud_usage

    async def get_storage_usage(self, db: AsyncSession, user_id: str) -> dict:
        """
        Get storage usage for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            {
                "used_bytes": 1024,
                "total_bytes": 10737418240,  # 10 GB
                "used_percentage": 0.01,
                "used_gb": 0.000001,
                "total_gb": 10.0
            }
        """
        from uuid import UUID
        
        # Get user to retrieve quota
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Calculate used storage (sum of all file sizes, excluding folders)
        usage_result = await db.execute(
            select(func.sum(File.size))
            .where(File.user_id == UUID(user_id), File.is_folder == False)
        )
        used_bytes = usage_result.scalar() or 0
        
        total_bytes = user.storage_quota_bytes
        
        # Calculate percentage
        used_percentage = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
        
        # Convert to GB for display
        used_gb = used_bytes / (1024 ** 3)
        total_gb = total_bytes / (1024 ** 3)
        
        # Get cloud storage usage
        cloud_usage = await self.get_cloud_storage_usage(db, user_id)
        
        return {
            "used_bytes": used_bytes,
            "total_bytes": total_bytes,
            "used_percentage": round(used_percentage, 2),
            "used_gb": round(used_gb, 2),
            "total_gb": round(total_gb, 2),
            "cloud_storage": cloud_usage,
        }
    
    async def check_storage_available(
        self, db: AsyncSession, user_id: str, file_size: int
    ) -> tuple[bool, int]:
        """
        Check if user has enough storage space for a file
        
        Args:
            db: Database session
            user_id: User ID
            file_size: Size of file to upload in bytes
            
        Returns:
            (is_available: bool, available_bytes: int)
        """
        usage = await self.get_storage_usage(db, user_id)
        available_bytes = usage["total_bytes"] - usage["used_bytes"]
        is_available = available_bytes >= file_size
        
        return is_available, available_bytes


storage_service = StorageService()
