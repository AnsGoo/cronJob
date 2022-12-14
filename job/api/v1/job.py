

from typing import Optional
from pydantic import ValidationError
from fastapi import APIRouter, Path, Query, Body, status, Response
from fastapi.exceptions import HTTPException
from zerorpc.core import Client
from app.common.resp_code import resp_200, resp_201, resp_202, resp_400
from app.common.logger import logger
from job.schemas import JobSchema, TriggerSchema, JobQueryParams
from apscheduler.job import Job
from utils.common import remove_none
from rpc.client import get_client
from app.config import settings

router = APIRouter()

def _get_job(job_id: str, client:Client) -> Job:
    job = client.get_job(job_id)
    if job:
        return job
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='%s not found' %job_id)


@router.get("/jobs", summary="获取所有job信息")
async def get_jobs(
        state: Optional[str] = Query(None, title='job 状态',description='可选参数 RUNNING STOP'),
        name: Optional[str] = Query(None, title='job name'),
        trigger: Optional[str] = Query(None, title='触发器类型', description='可选参数：date cron interval'),
        func: Optional[str] = Query(None, title='任务名称', description='任务的方法名称')
        ) -> Response:
    """
    获取所有job
    :return:
    """
    try:
        query_condtions = JobQueryParams(state=state, name=name, trigger=trigger, func=func)
    except ValidationError as e:
        return resp_400(e.json())
    with get_client(settings.RPC_URL) as client:
        conditions = remove_none(query_condtions.dict())
        jobs = client.query_jobs('default', conditions)
    return resp_200(data=jobs)


@router.get("/jobs/{job_id}", summary="获取指定的job信息")
async def get_job(
        job_id: str = Query("job_id", title="job id")
) -> Response:
    with get_client(settings.RPC_URL) as client:
        job = _get_job(job_id=job_id, client=client)
        return resp_200(job)


# cron 更灵活的定时任务 可以使用crontab表达式
@router.post("/jobs", summary='添加job')
async def add_job(job: JobSchema) -> Response:
    with get_client(settings.RPC_URL) as client:
        instance, msg = client.add_job(job.to_dict())
    if instance:
        return resp_201(instance)
    else:
        return resp_400(msg)


@router.delete("/job/{job_id}", summary="移除任务")
async def remove_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    try:
        with get_client(settings.RPC_URL) as client:
            result = client.remove_job(job_id, client=client)
            print(result)
    except Exception as e:
        logger.error(e)
        return resp_400()
    return resp_202()

@router.get("/job/{job_id}/pause", summary="暂停任务")
async def pause_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    with get_client(settings.RPC_URL) as client:
        job = _get_job(job_id=job_id, client=client)
        job = client.pause_job(job_id)
    return resp_202(job)


@router.get("/job/{job_id}/resume", summary="恢复任务")
async def resume_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    with get_client(settings.RPC_URL) as client:
        _get_job(job_id=job_id, client=client)
        job = client.resume_job(job_id)
    return resp_202(job)


@router.put("/job/{job_id}/reschedule", summary="重新调度任务")
async def reschedule_job(
        trigger: TriggerSchema,
        job_id: str = Path(...,title="任务id", embed=True),
        jobstore: Optional[str] = Body('default')
) -> Response:
    with get_client(settings.RPC_URL) as client: 
        _get_job(job_id=job_id, client=client)     
        job, result = client.reschedule_job(job_id, trigger.dict(), jobstore)
    return resp_202(job)


@router.get("/job/stores", summary="获取stores")
async def get_stores() -> Response:
    with get_client(settings.RPC_URL) as client:
        stores = client.get_stores()
    return resp_200(data=[{ 'name': item for item in stores}])


@router.get("/job/executors", summary="获取")
async def get_executors() -> Response:
    with get_client(settings.RPC_URL) as client:
        executors = client.get_executors()
    return resp_200(data=[{ 'name': item for item in executors}])
