import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.anomaly import get_anomaly_results
from app.cleanup import (
    cleanup_files,
    get_cleanup_candidates,
    is_cleanup_allowed,
)
from app.database import engine
from app.logger import get_logger
from app.models import CleanupAction
from app.repository import get_all_scans, save_scan
from app.scanner import (
    get_directories,
    get_directory_size,
    get_file_category_stats,
    get_file_type_stats,
    get_largest_files,
)
from app.system import get_disk_usage, get_status


SCAN_ROOT = os.getenv("SCAN_ROOT", "/home")


class SystemResponse(BaseModel):
    disk_usage_percent: float
    status: str
    total: float
    used: float
    free: float


class ScanResponse(BaseModel):
    id: int
    timestamp: datetime
    usage_percent: float
    total: float
    used: float
    free: float


class CleanupResponse(BaseModel):
    id: int
    file_path: str
    action: str
    timestamp: datetime
    status: str


class CleanupCandidatesResponse(BaseModel):
    total_candidates: int
    total_size_bytes: int
    offset: int
    limit: int
    candidates: list[str]


class CleanupRequest(BaseModel):
    file_path: str
    confirmed: bool = False


class CleanupResultResponse(BaseModel):
    status: str
    file: str


app = FastAPI(
    title="LinuxGuard API",
    description="Linux System Health and Storage Management API",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "LinuxGuard API is running"}


@app.get("/system", response_model=SystemResponse)
def system_status():
    usage = get_disk_usage()
    status = get_status(usage["percent"])

    return {
        "disk_usage_percent": usage["percent"],
        "status": status,
        "total": usage["total"],
        "used": usage["used"],
        "free": usage["free"],
    }


@app.post("/scan")
def create_scan():
    usage = get_disk_usage()
    status = get_status(usage["percent"])

    try:
        scan_id, _ = save_scan(engine, usage)
    except Exception as error:
        logger = get_logger()
        logger.error(f"SCAN | Database error | {error}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save scan",
        )

    return {
        "scan_id": scan_id,
        "disk_usage_percent": usage["percent"],
        "status": status,
        "total": usage["total"],
        "used": usage["used"],
        "free": usage["free"],
    }


@app.get("/scans", response_model=list[ScanResponse])
def scan_history():
    try:
        scans = get_all_scans(engine)
    except Exception as error:
        logger = get_logger()
        logger.error(f"SCAN HISTORY | Database error | {error}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve scan history",
        )

    return [
        {
            "id": scan.id,
            "timestamp": scan.timestamp,
            "usage_percent": scan.usage_percent,
            "total": scan.total_size,
            "used": scan.used_size,
            "free": scan.free_size,
        }
        for scan in scans
    ]


@app.get("/cleanup-history", response_model=list[CleanupResponse])
def cleanup_history():
    with Session(engine) as session:
        actions = session.query(CleanupAction).all()

        return [
            {
                "id": action.id,
                "file_path": action.file_path,
                "action": action.action,
                "timestamp": action.timestamp,
                "status": action.status,
            }
            for action in actions
        ]


@app.get(
    "/cleanup-candidates",
    response_model=CleanupCandidatesResponse,
)
def cleanup_candidates(limit: int = 50, offset: int = 0):
    candidates = get_cleanup_candidates(SCAN_ROOT)

    total_size = sum(
        file_path.stat().st_size
        for file_path in candidates
        if file_path.exists()
    )

    selected = candidates[offset:offset + limit]

    return {
        "total_candidates": len(candidates),
        "total_size_bytes": total_size,
        "offset": offset,
        "limit": limit,
        "candidates": [
            str(file_path)
            for file_path in selected
        ],
    }


@app.post("/cleanup", response_model=CleanupResultResponse)
def cleanup(request: CleanupRequest):
    file_path = Path(request.file_path)

    if not request.file_path.strip():
        raise HTTPException(
            status_code=422,
            detail="File path cannot be empty.",
        )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File does not exist.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Path is not a file.",
        )

    if not is_cleanup_allowed(file_path):
        raise HTTPException(
            status_code=403,
            detail="Cleanup not allowed for this path.",
        )

    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required before cleanup.",
        )

    deleted = cleanup_files(
        [file_path],
        dry_run=False,
        confirmed=True,
    )

    if deleted:
        return {
            "status": "success",
            "file": str(file_path),
        }

    raise HTTPException(
        status_code=500,
        detail="File could not be deleted.",
    )


@app.get("/storage-analysis")
def storage_analysis():
    path = SCAN_ROOT

    largest_files = get_largest_files(path, limit=10)
    file_types = get_file_type_stats(path)
    file_categories = get_file_category_stats(path)

    return {
        "path": path,
        "largest_files": largest_files,
        "file_types": file_types,
        "file_categories": file_categories,
    }


@app.get("/anomalies")
def anomalies():
    results = get_anomaly_results()

    return {
        "total_scans": len(results),
        "anomaly_count": sum(
            1 for result in results
            if result["anomaly"]
        ),
        "results": results,
    }
