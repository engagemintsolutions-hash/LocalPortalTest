"""
S3 Storage Manager for Property Listings and Images

Handles uploading property images and data to S3 with proper organization.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from io import BytesIO
import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

logger = logging.getLogger(__name__)


class S3StorageManager:
    """
    Manages storage of property listings and images in S3.

    Directory structure:
    s3://bucket/
    ├── listings/
    │   ├── raw/              # Raw scraped data JSON
    │   └── enriched/         # Enriched listing data
    └── images/
        └── {listing_id}/     # Images for each listing
            ├── main.jpg      # Primary image
            ├── 001.jpg       # Additional images
            ├── 002.jpg
            └── floor_plan.jpg
    """

    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 storage manager.

        Args:
            bucket_name: S3 bucket name. If None, uses env var PROPERTY_IMAGES_BUCKET
        """
        self.bucket = bucket_name or os.getenv('PROPERTY_IMAGES_BUCKET', 'uk-property-images')
        self.s3_client = boto3.client('s3')
        self.region = os.getenv('AWS_REGION', 'eu-west-2')

        # Verify bucket exists
        self._verify_bucket()

    def _verify_bucket(self):
        """Check if S3 bucket exists, create if not"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            logger.info(f"S3 bucket '{self.bucket}' verified")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"Bucket '{self.bucket}' not found. Creating...")
                self._create_bucket()
            else:
                raise

    def _create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            logger.info(f"Created S3 bucket: {self.bucket}")

            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )

        except ClientError as e:
            logger.error(f"Failed to create bucket: {e}")
            raise

    def upload_listing_images(
        self,
        listing_id: int,
        image_urls: List[str],
        agent_id: int
    ) -> List[str]:
        """
        Download images from URLs and upload to S3.

        Args:
            listing_id: Database listing ID
            image_urls: List of image URLs to download
            agent_id: Agent ID for organization

        Returns:
            List of S3 URLs for uploaded images
        """
        s3_urls = []

        for idx, image_url in enumerate(image_urls):
            try:
                # Download image
                logger.info(f"Downloading image {idx+1}/{len(image_urls)}: {image_url}")
                response = requests.get(image_url, timeout=30, stream=True)
                response.raise_for_status()

                # Determine filename
                if idx == 0:
                    filename = 'main.jpg'
                else:
                    filename = f"{idx:03d}.jpg"

                # Detect content type
                content_type = response.headers.get('Content-Type', 'image/jpeg')

                # Upload to S3
                s3_key = f"images/{agent_id}/{listing_id}/{filename}"
                s3_url = self._upload_file_object(
                    file_obj=BytesIO(response.content),
                    s3_key=s3_key,
                    content_type=content_type
                )

                s3_urls.append(s3_url)
                logger.info(f"Uploaded to S3: {s3_key}")

            except Exception as e:
                logger.error(f"Failed to upload image {image_url}: {e}")
                # Continue with other images
                continue

        return s3_urls

    def upload_floor_plan(
        self,
        listing_id: int,
        floor_plan_url: str,
        agent_id: int
    ) -> Optional[str]:
        """
        Upload floor plan image to S3.

        Args:
            listing_id: Database listing ID
            floor_plan_url: URL of floor plan image
            agent_id: Agent ID

        Returns:
            S3 URL of uploaded floor plan, or None if failed
        """
        try:
            response = requests.get(floor_plan_url, timeout=30, stream=True)
            response.raise_for_status()

            # Determine extension
            ext = floor_plan_url.split('.')[-1].split('?')[0]
            if ext not in ['jpg', 'jpeg', 'png', 'pdf']:
                ext = 'jpg'

            s3_key = f"images/{agent_id}/{listing_id}/floor_plan.{ext}"
            content_type = response.headers.get('Content-Type', 'image/jpeg')

            s3_url = self._upload_file_object(
                file_obj=BytesIO(response.content),
                s3_key=s3_key,
                content_type=content_type
            )

            logger.info(f"Uploaded floor plan to S3: {s3_key}")
            return s3_url

        except Exception as e:
            logger.error(f"Failed to upload floor plan {floor_plan_url}: {e}")
            return None

    def _upload_file_object(
        self,
        file_obj: BytesIO,
        s3_key: str,
        content_type: str = 'image/jpeg',
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file-like object to S3.

        Args:
            file_obj: File-like object (BytesIO)
            s3_key: S3 object key
            content_type: MIME type
            metadata: Optional metadata dict

        Returns:
            S3 URL of uploaded object
        """
        extra_args = {
            'ContentType': content_type,
            'CacheControl': 'max-age=31536000',  # 1 year cache
            'Metadata': metadata or {}
        }

        self.s3_client.upload_fileobj(
            file_obj,
            self.bucket,
            s3_key,
            ExtraArgs=extra_args
        )

        # Return S3 URL
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

    def upload_listing_json(
        self,
        listing_id: int,
        data: Dict[str, Any],
        listing_type: str = 'raw'  # 'raw' or 'enriched'
    ) -> str:
        """
        Upload listing data as JSON to S3.

        Args:
            listing_id: Database listing ID
            data: Listing data dictionary
            listing_type: 'raw' or 'enriched'

        Returns:
            S3 URL of uploaded JSON
        """
        import json

        s3_key = f"listings/{listing_type}/{listing_id}.json"

        # Add timestamp
        data['uploaded_at'] = datetime.utcnow().isoformat()

        # Upload JSON
        json_bytes = json.dumps(data, indent=2, default=str).encode('utf-8')

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=json_bytes,
            ContentType='application/json',
            Metadata={'listing_id': str(listing_id)}
        )

        logger.info(f"Uploaded {listing_type} listing JSON: {s3_key}")

        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

    def delete_listing_images(self, listing_id: int, agent_id: int):
        """
        Delete all images for a listing.

        Args:
            listing_id: Database listing ID
            agent_id: Agent ID
        """
        prefix = f"images/{agent_id}/{listing_id}/"

        try:
            # List all objects with prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )

            if 'Contents' not in response:
                logger.info(f"No images found for listing {listing_id}")
                return

            # Delete objects
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]

            self.s3_client.delete_objects(
                Bucket=self.bucket,
                Delete={'Objects': objects_to_delete}
            )

            logger.info(f"Deleted {len(objects_to_delete)} images for listing {listing_id}")

        except ClientError as e:
            logger.error(f"Failed to delete images for listing {listing_id}: {e}")

    def get_listing_image_urls(self, listing_id: int, agent_id: int) -> List[str]:
        """
        Get all S3 URLs for a listing's images.

        Args:
            listing_id: Database listing ID
            agent_id: Agent ID

        Returns:
            List of S3 URLs
        """
        prefix = f"images/{agent_id}/{listing_id}/"

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )

            if 'Contents' not in response:
                return []

            urls = [
                f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{obj['Key']}"
                for obj in response['Contents']
            ]

            # Sort to put main.jpg first
            urls.sort(key=lambda x: 'main.jpg' not in x)

            return urls

        except ClientError as e:
            logger.error(f"Failed to list images for listing {listing_id}: {e}")
            return []


# Singleton instance
_storage_manager: Optional[S3StorageManager] = None


def get_storage_manager() -> S3StorageManager:
    """Get or create the global S3 storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = S3StorageManager()
    return _storage_manager
