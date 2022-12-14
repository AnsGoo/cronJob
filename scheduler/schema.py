from typing import Any, Dict, Mapping, Optional
from pydantic import BaseModel, validator

from apscheduler.executors.pool import BasePoolExecutor, ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.base import BaseJobStore
from scheduler.stores import ExtendSQLAlchemyJobStore 

from enum import Enum

class ExcutorPool(Enum):
    thread = 'thread'
    process = 'process'


class JobExecutorPool(BaseModel):
    type: str = 'thread'
    size: int = 1
    
    @validator('size')
    def validate_size(cls, size: int, values: Optional[Dict]) -> int:
        if size > 0:
            return size
        else:
            raise ValueError('pool size must be more than 1')
        

    def build(self) -> BasePoolExecutor:
        if self.type == 'thread':
            return ThreadPoolExecutor(self.size)
        elif self.type == 'process':
            return ProcessPoolExecutor(self.size)
        else:
            raise NotImplementedError('%s executor are not implemente' % self.type )


class Store(Enum):
    sqlalchemy = 'sqlalchemy'
    redis = 'redis'
    mongo = 'mongo'


class JobStore(BaseModel):
    type: str = 'sqlalchemy'
    url: str
    
    def build(self) -> BaseJobStore:
        if self.type == 'sqlalchemy':
            return ExtendSQLAlchemyJobStore(self.url)
        else:
            raise NotImplementedError('%s store are not implemente' % self.type )

class Default(BaseModel):
    coalesce: bool = False
    max_instances: int = 1

class SchedulerConfig(BaseModel):
    executors: Mapping[str, Any]
    default: Mapping[str,Any]
    stores: Mapping[str, Any]


    @validator('executors', pre=True)
    def validate_executors(cls, executors: Mapping[str, JobExecutorPool], values: Optional[Dict]) -> Mapping[str,JobExecutorPool]:
        if 'default' in executors:
            return executors
        else:
            raise ValueError('default excutor must be exists')


    @validator('stores', pre=True)
    def validate_stores(cls, stores: Mapping[str, JobStore], values: Optional[Dict]) -> Mapping[str, JobStore]:
        if 'default' in stores:
            return stores
        else:
            raise ValueError('default excutor must be exists')