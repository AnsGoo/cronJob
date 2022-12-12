from __future__ import absolute_import
import six
from typing import Optional

from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.schedulers.base import STATE_STOPPED


class ExtendGeventcheduler(GeventScheduler):
    def query_jobs(self, jobstore: str='default', conditions: Optional[dict]=dict()):
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