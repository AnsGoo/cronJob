
import pdir
from scheduler.utils import job_to_dict
import uuid
from typing import Dict, Optional
from pydantic import ValidationError
from fastapi import APIRouter, Path, Query, Body, Request, status, Response
from fastapi.exceptions import HTTPException
from app.common.resp_code import resp_200, resp_201, resp_202, resp_400
from job.schemas import JobSchema, TriggerSchema, JobQueryParams
from apscheduler.job import Job
from scheduler.schedulers.asyncio import ExtendAsyncIOScheduler
from job.tasks import Task
from app.config import settings
from app.state import default_state
from utils.common import remove_none

router = APIRouter()
config = settings.SCHEDULER_CONFIG

schedule = ExtendAsyncIOScheduler(
            jobstores=config.stores, 
            executors=config.executors, 
            job_defaults=config.default
        )

def _get_job(job_id: str) -> Job:
    schedule = default_state.get('schedule')
    job = schedule.get_job(job_id)
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
    schedule = default_state.get('schedule')
    try:
        query_params =  request.query_params._dict
        query_condtions = JobQueryParams(**query_params)
    except ValidationError as e:
        return resp_400(e.errors())
    jobs = schedule.query_jobs(conditions=remove_none(query_condtions.dict()))
    data = [job_to_dict(job) for job in jobs]
    return resp_200(data=data)


@router.get("/jobs/{job_id}", tags=["job"], summary="获取指定的job信息")
async def get_job(
        job_id: str = Query("job_id", title="job id")
) -> Response:
    job = _get_job(job_id=job_id)
    return resp_200(job_to_dict(job))


# cron 更灵活的定时任务 可以使用crontab表达式
@router.post("/jobs/", tags=["job"], summary='添加job')
async def add_job(job: JobSchema = Body(..., embed=True)) -> Response:
    job_id = str(uuid.uuid1())
    schedule = default_state.get('schedule')
    schedule_job = schedule.add_job(
        func=job.func,
        trigger=job.trigger.build(),
        args=job.args,
        kwargs=job.kwargs,
        id=job_id,
        name=job.name,
        misfire_grace_time=job.misfire_grace_time,
        coalesce=job.coalesce,
        max_instances=job.max_instances,
        next_run_time=job.next_run_time,
        jobstore=job.jobstore,
        executor=job.executor,
        replace_existing=job.replace_existing
        )
    return resp_201(job_to_dict(schedule_job))


@router.delete("/job/{job_id}/", tags=["job"], summary="移除任务")
async def remove_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    _get_job(job_id=job_id)
    schedule = default_state.get('schedule')
    schedule.remove_job(job_id)
    return resp_202('OK')


@router.get("/job/{job_id}/pause/", tags=["job"], summary="暂停任务")
async def pause_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    job = _get_job(job_id=job_id)
    schedule = default_state.get('schedule')
    schedule.pause_job(job_id)
    job = _get_job(job_id=job_id)
    return resp_202(job_to_dict(job))


@router.get("/job/{job_id}/resume/", tags=["job"], summary="恢复任务")
async def resume_job(
        job_id: str = Path(..., title="任务id", embed=True)
) -> Response:
    _get_job(job_id=job_id)
    schedule = default_state.get('schedule')
    schedule.resume_job(job_id)
    job = _get_job(job_id=job_id)
    return resp_202(job_to_dict(job))


@router.put("/job/{job_id}/reschedule/", tags=["job"], summary="重新调度任务")
async def reschedule_job(
        job_id: str = Path(...,title="任务id", embed=True),
        trigger: TriggerSchema = Body(..., embed=True),
        jobstore: str = Body('default',title="存储器", embed=True)
) -> Response:
    _get_job(job_id=job_id)
    schedule = default_state.get('schedule')
    schedule.reschedule_job(job_id, jobstore=jobstore, trigger=trigger)
    job = _get_job(job_id=job_id)
    return resp_202(job_to_dict(job))


@router.get("/job/stores", tags=["job"], summary="获取stores")
async def get_stores() -> Response:
    schedule = default_state.get('schedule')
    stores = list(schedule._jobstores.keys())
    return resp_200(data=stores)


@router.get("/job/executors", tags=["job"], summary="获取")
async def get_executors() -> Response:
    schedule = default_state.get('schedule')
    executors = list(schedule._executors.keys())
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
