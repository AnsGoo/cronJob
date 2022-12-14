from fastapi import APIRouter
from .api.v1.job import router as job_router
from .api.v1.record import router as record_router
from .api.v1.task import router as task_router

router = APIRouter()

router.include_router(job_router, tags=["job"])
router.include_router(record_router, tags=["record"])
router.include_router(task_router, tags=["task"])