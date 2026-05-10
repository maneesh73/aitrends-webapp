from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import get_db
from models import SyncJobConfig
from auth import require_sync_auth
import scheduler as sched

router = APIRouter(prefix="/api/admin", tags=["admin"])


class JobConfigUpdate(BaseModel):
    cron_expr: str
    enabled: bool


class JobSource(BaseModel):
    name: str
    type: str
    note: Optional[str] = None


class JobStatus(BaseModel):
    id: str
    name: str
    description: str
    cron_expr: str
    enabled: bool
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    last_run_message: Optional[str]
    next_run_at: Optional[datetime]
    sources: List[JobSource]


@router.get("/jobs", response_model=List[JobStatus], dependencies=[Depends(require_sync_auth)])
def list_jobs(db: Session = Depends(get_db)):
    results = []
    for job_id, defn in sched.JOB_DEFINITIONS.items():
        cfg = db.query(SyncJobConfig).filter(SyncJobConfig.id == job_id).first()
        next_run = sched.get_next_run(job_id)
        results.append(JobStatus(
            id=job_id,
            name=defn["name"],
            description=defn["description"],
            cron_expr=cfg.cron_expr if cfg else defn["default_cron"],
            enabled=cfg.enabled if cfg else False,
            last_run_at=cfg.last_run_at if cfg else None,
            last_run_status=cfg.last_run_status if cfg else None,
            last_run_message=cfg.last_run_message if cfg else None,
            next_run_at=next_run,
            sources=[JobSource(**s) for s in defn["sources"]],
        ))
    return results


@router.put("/jobs/{job_id}", response_model=JobStatus, dependencies=[Depends(require_sync_auth)])
def update_job(job_id: str, body: JobConfigUpdate, db: Session = Depends(get_db)):
    if job_id not in sched.JOB_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        from apscheduler.triggers.cron import CronTrigger
        CronTrigger.from_crontab(body.cron_expr)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cron expression")

    cfg = db.query(SyncJobConfig).filter(SyncJobConfig.id == job_id).first()
    if not cfg:
        cfg = SyncJobConfig(id=job_id)
        db.add(cfg)

    cfg.cron_expr = body.cron_expr
    cfg.enabled = body.enabled
    db.commit()
    db.refresh(cfg)

    sched.reschedule_job(job_id, body.cron_expr, body.enabled)

    defn = sched.JOB_DEFINITIONS[job_id]
    next_run = sched.get_next_run(job_id)
    return JobStatus(
        id=job_id,
        name=defn["name"],
        description=defn["description"],
        cron_expr=cfg.cron_expr,
        enabled=cfg.enabled,
        last_run_at=cfg.last_run_at,
        last_run_status=cfg.last_run_status,
        last_run_message=cfg.last_run_message,
        next_run_at=next_run,
        sources=[JobSource(**s) for s in defn["sources"]],
    )


@router.post("/jobs/{job_id}/run", dependencies=[Depends(require_sync_auth)])
def trigger_job(job_id: str):
    if job_id not in sched.JOB_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Job not found")
    ok = sched.run_job_now(job_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to trigger job")
    return {"status": "triggered", "job_id": job_id}
