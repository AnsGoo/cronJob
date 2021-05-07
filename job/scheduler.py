from __future__ import absolute_import

import six
import json
from typing import Optional

from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from apscheduler.util import maybe_ref, datetime_to_utc_timestamp
from apscheduler.events import EVENT_JOB_MISSED,EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, SchedulerEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.base import STATE_STOPPED
from apscheduler.job import Job

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from sqlalchemy import (
        create_engine, Table, Column, MetaData, Unicode, Float, LargeBinary, select, String, Enum)
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.expression import null
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')

from app.common.logger import logger

from .utils import get_job_trigger_name, job_to_dict
from .models import JobRecord
from app.core.config import settings
from .tasks import Task
from app.database import db


class ExtendAsyncIOScheduler(AsyncIOScheduler):
    def query_jobs(self, jobstore: str=None, conditions: Optional[dict]=dict()):
        with self._jobstores_lock:
            jobs = []
            if self.state == STATE_STOPPED:
                for job, alias, replace_existing in self._pending_jobs:
                    if jobstore is None or alias == jobstore:
                        jobs.append(job)
            else:
                for alias, store in six.iteritems(self._jobstores):
                    if jobstore is None or alias == jobstore:

                        jobs.extend(store.query_jobs(**conditions))
            return jobs

class ExtendSQLAlchemyJobStore(SQLAlchemyJobStore):
    def __init__(self, url=None, engine=None, tablename='apscheduler_jobs', metadata=None,
                 pickle_protocol=pickle.HIGHEST_PROTOCOL, tableschema=None, engine_options=None):
        self.pickle_protocol = pickle_protocol
        metadata = maybe_ref(metadata) or MetaData()
        if engine:
            self.engine = maybe_ref(engine)
        elif url:
            self.engine = create_engine(url, **(engine_options or {}))
        else:
            raise ValueError('Need either "engine" or "url" defined')

        sessionLocal = sessionmaker(bind=self.engine)
        self.db = sessionLocal()
        self.jobs_t = Table(
            tablename, metadata,
            Column('id', Unicode(191, _warn_on_bytestring=False), primary_key=True),
            Column('name', String(256)),
            Column('func', String(256)),
            Column('trigger', Enum('date', 'cron', 'interval')),
            Column('next_run_time', Float(25), index=True),
            Column('job_state', LargeBinary, nullable=False),
            schema=tableschema
        )

    def add_job(self, job: Job) -> None:
        insert = self.jobs_t.insert().values(**{
            'id': job.id,
            'name': job.name,
            'trigger': get_job_trigger_name(job.trigger),
            'func': job.func.__name__,
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol)
        })
        try:
            self.engine.execute(insert)
        except IntegrityError:
            raise ConflictingIdError(job.id)

    def update_job(self, job: Job) -> None:
        update = self.jobs_t.update().values(**{
            'name': job.name,
            'trigger': get_job_trigger_name(job.trigger),
            'func': job.func.__name__,
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol)
        }).where(self.jobs_t.c.id == job.id)
        result = self.engine.execute(update)
        if result.rowcount == 0:
            raise JobLookupError(job.id)

    def query_jobs(self, **conditions):
        jobs = self._query_jobs(**conditions)
        self._fix_paused_jobs_sorting(jobs)
        return jobs

    def _query_jobs(self, **conditions):
        jobs = []
        queryset = self.db.query(self.jobs_t).order_by(self.jobs_t.c.next_run_time)
        state = conditions.pop('state', None)
        if conditions:
            queryset = queryset.filter_by(**conditions)
        if state is not None:
            if state:
                queryset = queryset.filter(self.jobs_t.c.next_run_time.isnot(None))
            else:
                queryset = queryset.filter(self.jobs_t.c.next_run_time==None)

        queryset = queryset.all()
        failed_job_ids = set()
        for row in queryset:
            try:
                jobs.append(self._reconstitute_job(row.job_state))
            except BaseException:
                self._logger.exception('Unable to restore job "%s" -- removing it', row.id)
                failed_job_ids.add(row.id)

        # Remove all the jobs we failed to restore
        if failed_job_ids:
            delete = self.jobs_t.delete().where(self.jobs_t.c.id.in_(failed_job_ids))
            self.engine.execute(delete)

        return jobs

executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(3)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 3
}

jobstores = {
    'default': ExtendSQLAlchemyJobStore(url=settings.DATABASE_URI)
}
schedule = ExtendAsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)


def save_record(event: SchedulerEvent, job: Job):

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


def job_lister(event: SchedulerEvent):
    job = schedule.get_job(event.job_id)
    save_record(event, job)
    if event.code == EVENT_JOB_EXECUTED:
        logger.info('job[%s] %s run SUCCESS at %s'%(job.id, job.name, event.scheduled_run_time))
    elif event.code == EVENT_JOB_ERROR:
        logger.error('job[%s] %s run FAILED at %s, error info: \n %s'%(job.id, job.name, event.scheduled_run_time, event.traceback))
    elif event.code == EVENT_JOB_MISSED:
        logger.warning('job[%s] %s run MISSED at %s'%(job.id, job.name, event.scheduled_run_time))





schedule.add_listener(job_lister, EVENT_JOB_EXECUTED|EVENT_JOB_ERROR|EVENT_JOB_MISSED)