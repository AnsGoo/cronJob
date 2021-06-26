from typing import Dict, List
from scheduler.task import BaseTask

class Task(BaseTask):
    def task_test(self) -> None:
        '''
        测试任务
        :return:
        '''
        print('test')

    def task_test1(self,job_id: str) -> None:
        '''
        测试任务1
        :return:
        '''
        print('task %s'%job_id)