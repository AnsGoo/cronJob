from fastapi import APIRouter
from .api.v1.job import router as job_router
from .api.v1.record import router as record_router

router = APIRouter()

router.include_router(job_router)
router.include_router(record_router)