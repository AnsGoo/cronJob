from datetime import date, datetime
from typing import Optional, List, Dict, Union, Any
from apscheduler.triggers.cron.fields import (
    BaseField, MonthField, DayOfMonthField, DayOfWeekField, DEFAULT_VALUES)
from apscheduler.util import undefined
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from pydantic import BaseModel, validator, conint

from .tasks import Task

class TriggerSchema(BaseModel):
    trigger: str
    run_time: str
    start_date: Optional[Union[datetime, date]] = None
    end_date: Optional[Union[datetime, date]] = None
    timezone: Optional[str] = None
    jitter: Optional[int] = None

    @validator('trigger',pre=True)
    def validate_trigger(cls, trigger: str, values: Optional[Dict]) -> str:
        if trigger in ['date','interval','cron']:
          return trigger
        else:
            raise ValueError('trigger must be in  date 、 interval and cron among')


    @validator('run_time')
    def validate_run_time(cls, run_time:str, values: Dict) -> str:
        if values['trigger'] == 'date':
            try:
                datetime.strptime(run_time, '%Y-%m-%d %H:%M:%S')
                return run_time
            except:
                try:
                    date.strftime(run_time, '%Y-%m-%d')
                    return run_time
                except:
                    raise ValueError('runtime must be date or datetime type')
        elif values['trigger'] == 'interval':
            datas = run_time.split()
            if len(datas) == 5:
                for item in datas:
                    if not item.isdigit():
                        ValueError('interval time must be consist of integer')
                return run_time
            else:
                raise ValueError('run time must format 0 0 1 0 0')

        elif values['trigger'] == 'cron':
            times = run_time.split()
            try:
                if len(times) in  [5,  6]:
                    second = BaseField('second', times[0])
                    minute = BaseField('minute', times[1])
                    hour = BaseField('hour', times[2])
                    day = DayOfMonthField('day', times[3])
                    month = MonthField('month', times[4])
                    day_of_week = DayOfWeekField('day_of_week', times[5])
                if len(times) == 6:
                    year = BaseField('year', times[6])
                return run_time
            except Exception as e:
                print(e)
                raise ValueError(str(e))

    def build(self) -> Union[DateTrigger, IntervalTrigger, CronTrigger]:
        if self.trigger == 'date':
            try:
                rundate = datetime.strptime(self.run_time, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    rundate = date.strftime(self.run_time, '%Y-%m-%d')
                except:
                    raise ValueError('runtime must be date or datetime type')

            return DateTrigger(run_date=rundate,timezone=self.timezone)

        elif self.trigger == 'interval':
            datas = self.run_time.split()
            data = [int(item) for item in datas]
            return IntervalTrigger(
                seconds=data[0],
                minutes=data[1],
                hours=data[2],
                days=data[3],
                weeks=data[4],
                start_date=self.start_date,
                end_date=self.end_date,
                timezone=self.timezone,
                jitter=self.jitter
            )

        elif self.trigger == 'cron':
            times = self.run_time.split()
            if len(times) == 5:
                return CronTrigger(
                    day_of_week=times[5],
                    month=times[4],
                    day=times[3],
                    hour=times[2],
                    minute=times[1],
                    second=times[0],
                    start_date=self.start_date,
                    end_date=self.end_date,
                    timezone=self.timezone,
                    jitter=self.jitter
                )
            elif len(times) == 6:
                return CronTrigger(
                    year=times[6],
                    day_of_week=times[5],
                    month=times[4],
                    day=times[3],
                    hour=times[2],
                    minute=times[1],
                    second=times[0],
                    start_date=self.start_date,
                    end_date=self.end_date,
                    timezone=self.timezone,
                    jitter=self.jitter
                )



class JobSchema(BaseModel):
    func: str
    name: str
    trigger: TriggerSchema
    max_instances: Optional[int] = 1
    args: Optional[List] = list()
    kwargs: Optional[Dict] = dict()
    next_run_time: Optional[Union[datetime, date]]
    jobstore: Optional[str] = 'default'
    executor: Optional['str'] = 'default'
    replace_existing: Optional[bool] = False
    misfire_grace_time: Optional[int]
    coalesce: Optional[bool]

    # misfire_grace_time = undefined, coalesce = undefined, max_instances = undefined,
    # next_run_time = undefined,

    def to_dict(self) -> Dict[str, Any]:
        data = self.dict()
        keys = list(data.keys())
        for k in keys:
            if data[k] == undefined:
                data.pop(k)
        
        data["func"] = self.func.__name__
        print(222, type(data))
        return data

    @validator('next_run_time', always=True)
    def validate_next_run_time(cls, next_run_time:datetime, values: Optional[Dict]) -> str:
        if not next_run_time is None:
            return next_run_time
        else:
            return undefined

    @validator('misfire_grace_time', always=True)
    def validate_misfire_grace_time(cls, misfire_grace_time: int, values: Optional[Dict]) -> str:
        if not misfire_grace_time is None:
            return misfire_grace_time
        else:
            return undefined


    @validator('coalesce', always=True)
    def validate_coalesce(cls, coalesce: int, values: Optional[Dict]) -> str:
        if not coalesce is None:
            return coalesce
        else:
            return undefined


    @validator('max_instances', always=True)
    def validate_max_instances(cls, max_instances: int, values: Optional[Dict]) -> int:
        if max_instances is None:
            return undefined
        else:
            return max_instances

    @validator('func')
    def validate_func(cls, func: str, values: Optional[Dict]) -> str:
        if func in Task().methods():
            return getattr(Task(),func)
        else:
            raise ValueError('not found %s task'%func)


class JobQueryParams(BaseModel):
    state: Optional[str]
    name: Optional[str]
    trigger: Optional[str]
    func: Optional[str]


    @validator('state', pre=True)
    def validate_state(cls, state: str, values: Optional[Dict]) -> Optional[bool]:
        if state == 'RUNNING':
            return True
        elif state == 'STOP':
            return False
        else:
            return None

class RecordQueryParams(BaseModel):
    result: Optional[str]
    name: Optional[str]
    trigger: Optional[str]
    page: Optional[conint(gt=0)]
    page_size: Optional[conint(gt=0)]




