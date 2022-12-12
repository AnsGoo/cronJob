
import six
import dateutil.parser
from datetime import datetime
from typing import Union, Dict, Tuple


from collections import OrderedDict
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from scheduler.task import BaseTask


def get_job_trigger_name(trigger: Union[CronTrigger, IntervalTrigger, DateTrigger]) -> str:
    if isinstance(trigger, DateTrigger):
        return 'date'
    elif isinstance(trigger, IntervalTrigger):
        return 'interval'
    elif isinstance(trigger, CronTrigger):
        return 'cron'


def job_to_dict(job:Job) -> Dict:
    """Converts a job to an OrderedDict."""
    args = []
    if len(job.args) > 1:
        args = [arg for arg in job.args if not isinstance(arg,BaseTask)]
    data = OrderedDict()
    data['id'] = job.id
    data['name'] = job.name
    data['func'] = job.func_ref
    data['args'] = args
    data['kwargs'] = job.kwargs
    data['jobstore'] = job._jobstore_alias

    data.update(trigger_to_dict(job.trigger))

    if not job.pending:
        data['misfire_grace_time'] = job.misfire_grace_time
        data['max_instances'] = job.max_instances
        data['next_run_time'] = None if job.next_run_time is None else job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")

    return data


def pop_trigger(data:Dict) -> Tuple[str]:
    """Pops trigger and trigger args from a given dict."""

    trigger_name = data.pop('trigger')
    trigger_args = {}

    if trigger_name == 'date':
        trigger_arg_names = ('run_date', 'timezone')
    elif trigger_name == 'interval':
        trigger_arg_names = ('weeks', 'days', 'hours', 'minutes', 'seconds', 'start_date', 'end_date', 'timezone')
    elif trigger_name == 'cron':
        trigger_arg_names = ('year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second', 'start_date', 'end_date', 'timezone')
    else:
        raise Exception('Trigger %s is not supported.' % trigger_name)

    for arg_name in trigger_arg_names:
        if arg_name in data:
            trigger_args[arg_name] = data.pop(arg_name)

    return trigger_name, trigger_args


def trigger_to_dict(trigger: Union[DateTrigger, IntervalTrigger, CronTrigger]) -> Dict:
    """Converts a trigger to an OrderedDict."""

    data = OrderedDict()

    if isinstance(trigger, DateTrigger):
        data['trigger'] = 'date'
        data['run_date'] = trigger.run_date.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(trigger, IntervalTrigger):
        data['trigger'] = 'interval'
        data['start_date'] = trigger.start_date.strftime("%Y-%m-%d %H:%M:%S")

        if trigger.end_date:
            data['end_date'] = trigger.end_date.strftime("%Y-%m-%d %H:%M:%S")
        times = [str(item) for item in extract_timedelta(trigger.interval)]
        times.reverse()
        data['run_time'] = ' '.join(times)

    elif isinstance(trigger, CronTrigger):
        data['trigger'] = 'cron'

        if trigger.start_date:
            data['start_date'] = trigger.start_date

        if trigger.end_date:
            data['end_date'] = trigger.end_date
        trigger.fields.reverse()
        cron = dict()
        for field in trigger.fields:
            if not field.is_default:
                    cron[field.name] = str(field)
        fields= ['second', 'minute', 'hour', 'day', 'month', 'day_of_week', 'year']
        times = [cron[field] for field in fields if cron.get(field)]
        data['run_time'] = ' '.join(times)
    else:
        data['trigger'] = str(trigger)

    return data


def fix_job_def(job_def:Dict) -> Dict:
    """
    Replaces the datetime in string by datetime object.
    """
    if six.PY2 and isinstance(job_def.get('func'), six.text_type):
        job_def['func'] = str(job_def.get('func'))

    if isinstance(job_def.get('start_date'), six.string_types):
        job_def['start_date'] = dateutil.parser.parse(job_def.get('start_date'))

    if isinstance(job_def.get('end_date'), six.string_types):
        job_def['end_date'] = dateutil.parser.parse(job_def.get('end_date'))

    if isinstance(job_def.get('run_date'), six.string_types):
        job_def['run_date'] = dateutil.parser.parse(job_def.get('run_date'))

    if isinstance(job_def.get('trigger'), dict):
        trigger = job_def.pop('trigger')
        job_def['trigger'] = trigger.pop('type', 'date')
        job_def.update(trigger)


def extract_timedelta(delta: datetime) -> Tuple[int]:
    w, d = divmod(delta.days, 7)
    mm, ss = divmod(delta.seconds, 60)
    hh, mm = divmod(mm, 60)
    return w, d, hh, mm, ss