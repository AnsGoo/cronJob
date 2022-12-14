import requests

class TestTask:
    @staticmethod
    def task_test(*args, **kwargs) -> None:
        '''
        测试任务
        :return:
        '''
        print('执行test')

    @staticmethod
    def task_test1(*args, **kwargs) -> None:
        '''
        测试任务1
        :return:
        '''
        print('执行结果test1')