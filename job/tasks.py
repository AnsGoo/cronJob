

class Task:
    def task_test(self):
        '''
        测试任务
        :return:
        '''
        print('test')

    def task_test1(self,job_id):
        '''
        测试任务1
        :return:
        '''
        print('task %s'%job_id)

    def methods(self):
        return (list(filter(lambda m: m.startswith("task") and not m.endswith("__") and callable(getattr(self, m)),
                            dir(self))))