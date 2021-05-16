
from __future__ import absolute_import
import pickle
from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
from apscheduler.util import maybe_ref, datetime_to_utc_timestamp
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.job import Job

try:
    from sqlalchemy import (
        create_engine, Table, Column, MetaData, Unicode, Float, LargeBinary, String, Enum)
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm.query import Query
    from sqlalchemy.exc import IntegrityError
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')

from scheduler.utils import get_job_trigger_name

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


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

    def query_jobs(self, **conditions) -> Query:
        jobs = self._query_jobs(**conditions)
        self._fix_paused_jobs_sorting(jobs)
        return jobs

    def _query_jobs(self, **conditions) -> Query:
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
