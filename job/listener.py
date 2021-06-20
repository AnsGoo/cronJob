import json
from apscheduler.job import Job
from apscheduler.events import EVENT_JOB_MISSED,EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobEvent
from scheduler.utils import get_job_trigger_name
from scheduler.listener import JobBaseListener
from app.database import db
from app.common.logger import logger
from .models import JobRecord
from .tasks import Task




class CornJobListener(JobBaseListener):

    def save_record(self,event: JobEvent, job: Job) -> None:

        result = None
        if event.code == EVENT_JOB_EXECUTED:
            result = 'SUCCESS'
        elif event.code == EVENT_JOB_ERROR:
            result = 'FAILED'
        elif event.code == EVENT_JOB_MISSED:
            result = 'MISSED'

        args = []
        if len(job.args) > 1:
            args = [arg for arg in job.args if not isinstance(arg,Task)]

        data = {
                'job_id': job.id,
                'name': job.name,
                'args': json.dumps(args),
                'kwargs': json.dumps(job.kwargs),
                'trigger': get_job_trigger_name(job.trigger),
                'result': result,
                'out': event.traceback,
                'runtime': event.scheduled_run_time
            }
        record = JobRecord(**data)
        db.add(record)
        db.commit()
        db.flush()

    def job_listener(self,event: JobEvent) -> None:
        job = self.schedule.get_job(event.job_id)
        self.save_record(event, job)
        if event.code == EVENT_JOB_EXECUTED:
            logger.info('job[%s] %s run SUCCESS at %s'%(event.job_id, job.name, event.scheduled_run_time))
        elif event.code == EVENT_JOB_ERROR:
            logger.error('job[%s] %s run FAILED at %s, error info: \n %s'%(event.job_id, job.name, event.scheduled_run_time, event.traceback))
        elif event.code == EVENT_JOB_MISSED:
            logger.warning('job[%s] %s run MISSED at %s'%(event.job_id, job.name, event.scheduled_run_time))
