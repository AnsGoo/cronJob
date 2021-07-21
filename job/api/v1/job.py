

from typing import Dict, Optional
from pydantic import ValidationError
from fastapi import APIRouter, Path, Query, Body, Form, Request, status, Response
from fastapi.exceptions import HTTPException
from zerorpc.core import Client
from app.common.resp_code import resp_200, resp_201, resp_202, resp_400
from job.schemas import JobSchema, TriggerSchema, JobQueryParams
from apscheduler.job import Job
from job.tasks import Task
from utils.common import remove_none
from rpc.client import get_client
from app.config import settings

router = APIRouter()

def _get_job(job_id: str, client:Client=None) -> Job:
    job = client.get_job(job_id)
    if job:
        return job
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='%s not found' %job_id)



@router.get("/jobs/", tags=["job"], summary="获取所有job信息")
async def get_jobs(
        request: Request,
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
        query_params =  request.query_params._dict
        query_condtions = JobQueryParams(**query_params)
    except ValidationError as e:
        return resp_400(e.errors())
    with get_client(settings.RPC_URL) as client:
        conditions = remove_none(query_condtions.dict())
        jobs = client.query_jobs('default', conditions)
    return resp_200(data=jobs)


@router.get("/jobs/{job_id}", tags=["job"], summary="获取指定的job信息")
async def get_job(
        job_id: str = Query("job_id", title="job id")
) -> Response:
    with get_client(settings.RPC_URL) as client:
        job = _get_job(job_id=job_id, client=client)
    return resp_200(job)


# cron 更灵活的定时任务 可以使用crontab表达式
@router.post("/jobs/", tags=["job"], summary='添加job')
async def add_job(request: Request,job: JobSchema) -> Response:
    data = await request.json()
    with get_client(settings.RPC_URL) as client:
        instance, msg = client.add_job(data)
    if instance:
        return resp_201(instance)
    else:
        return resp_400(msg)


@router.delete("/job/{job_id}/", tags=["job"], summary="移除任务")
async def remove_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    _get_job(job_id=job_id)
    with get_client(settings.RPC_URL) as client:
        result = client.remove_job(job_id, client=client)
    return resp_202(result)

@router.get("/job/{job_id}/pause/", tags=["job"], summary="暂停任务")
async def pause_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    with get_client(settings.RPC_URL) as client:
        job = _get_job(job_id=job_id, client=client)
        job = client.pause_job(job_id)
    return resp_202(job)


@router.get("/job/{job_id}/resume/", tags=["job"], summary="恢复任务")
async def resume_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    with get_client(settings.RPC_URL) as client:
        _get_job(job_id=job_id, client=client)
        job = client.resume_job(job_id)
    return resp_202(job)


@router.put("/job/{job_id}/reschedule/", tags=["job"], summary="重新调度任务")
async def reschedule_job(
        request: Request,
        trigger: TriggerSchema,
        job_id: str = Path(...,title="任务id", embed=True),
        jobstore: Optional[str] = Body('default')
) -> Response:
    with get_client(settings.RPC_URL) as client: 
        _get_job(job_id=job_id, client=client)
        data = await request.json()
        job = client.reschedule_job(job_id, jobstore=jobstore, trigger=data)
    return resp_202(job)


@router.get("/job/stores", tags=["job"], summary="获取stores")
async def get_stores() -> Response:
    with get_client(settings.RPC_URL) as client:
        stores = client.get_stores()
    return resp_200(data=stores)


@router.get("/job/executors", tags=["job"], summary="获取")
async def get_executors() -> Response:
    with get_client(settings.RPC_URL) as client:
        executors = client.get_executors()
    return resp_200(data=executors)

@router.get("/job/tasks", tags=["job"], summary="获取可用Task")
async def get_tasks() -> Response:
    tasks = Task().methods()
    data = []
    for task in tasks:
        data.append(
            {
                'name': task,
                'desc': getattr(Task(),task).__doc__
            }
        )
    return resp_200(data=data)
