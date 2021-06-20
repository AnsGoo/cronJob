import uuid
from enum import Enum
from pydantic import ValidationError
from typing import Dict, List, Tuple
from scheduler.utils import job_to_dict
from job.schemas import JobSchema, TriggerSchema
from app.common.logger import logger


class Result(Enum):
    sucess = 'Success'
    fail = 'fail'


class SchedulerService:
    def __init__(self, scheduler) -> None:
        self.scheduler = scheduler

    def add_job(self, data:Dict) -> Tuple:
        job_id = str(uuid.uuid1())
        try:
            schema = JobSchema(**data)
        except ValidationError as e:
            logger.warning('create job fail', e.json())
            return None, e.json()

        job = self.scheduler.add_job(
            func=schema.func,
            trigger=schema.trigger.build(),
            args=schema.args,
            kwargs=schema.kwargs,
            id=job_id,
            name=schema.name,
            misfire_grace_time=schema.misfire_grace_time,
            coalesce=schema.coalesce,
            max_instances=schema.max_instances,
            next_run_time=schema.next_run_time,
            jobstore=schema.jobstore,
            executor=schema.executor,
            replace_existing=schema.replace_existing
        )
        return job_to_dict(job), Result.sucess.value
    
    def reschedule_job(self, job_id:str, trigger:Dict,jobstore=None) ->Dict:
        try:
            schema = TriggerSchema(**trigger)
        except ValidationError as e:
            return None, e.json()

        job = self.scheduler.reschedule_job(job_id, jobstore, trigger=schema)
        return job_to_dict(job), Result.sucess.value

    def pause_job(self, job_id:str, jobstore:str=None) -> Dict:
        logger.info('job[%s] has been paused' %job_id)
        job = self.scheduler.pause_job(job_id, jobstore)
        return job_to_dict(job)

    def resume_job(self, job_id:str, jobstore:str=None) -> Dict :
        logger.info('job[%s] has been resumed' %job_id)
        job = self.scheduler.resume_job(job_id, jobstore)
        return job_to_dict(job)

    def remove_job(self, job_id:str, jobstore:str=None) -> str:
        logger.info('job[%s] has been removed' %job_id)
        self.scheduler.remove_job(job_id, jobstore)
        return Result.sucess

    def get_job(self, job_id:str) -> Dict:
        job = self.scheduler.get_job(job_id)
        return job_to_dict(job)

    def get_jobs(self, jobstore:str=None) -> List[Dict]:
        jobs = self.scheduler.get_jobs(jobstore)
        data = [job_to_dict(job) for job in jobs]
        return data

    def query_jobs(self, jobstore:str, conditions:Dict=dict())  -> List[Dict]:
        jobs = self.scheduler.query_jobs(jobstore=jobstore,conditions=conditions)
        data = [job_to_dict(job) for job in jobs]
        return data
        
    def get_stores(self) -> List[str]:
        return list(self.scheduler._jobstores.keys())

    def get_excutors(self) -> List[str]:
        return list(self.scheduler._executors.keys())