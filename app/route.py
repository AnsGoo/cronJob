from fastapi import APIRouter

from job.route import router as job_router

router = APIRouter()
router.include_router(job_router,prefix='/v1')

