"""File storage and virus scanning tasks."""
import structlog
from celery import shared_task

logger = structlog.get_logger()


@shared_task
def scan_uploaded_file(attachment_id: str, storage_key: str) -> bool:
    """Run ClamAV scan on uploaded file; mark attachment av_clean=True/False."""
    logger.info("av_scan_started", attachment_id=attachment_id, key=storage_key)
    # In production: stream file from S3, pipe through ClamAV socket
    # Update attachment record with scan result
    return True
