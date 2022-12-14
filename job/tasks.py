
import inspect
import importlib
import threading
from app.config import settings

class Singleton(type):
    _instance_lock = threading.Lock()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def __call__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not hasattr(cls, '_instance'):
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
        

class TaskCollection(metaclass=Singleton):
    def __init__(self) -> None:
        self.task_dict = {}
        self.load_task()

    def load_task(self):
        for file in settings.TASK_SCRIPT_PATH.glob('*.py'):
            key = f'task.{file.stem}'
            module = importlib.import_module(key)
            class_list = inspect.getmembers(module, inspect.isclass)
            for cs in class_list:
                if 'Task' in cs[0]:
                    key = f'{key}.{cs[0]}'
                    func_list = inspect.getmembers(cs[1], inspect.isfunction)
                    for func in func_list:
                        if func[0].startswith('task_'):
                            key = f'{key}.{func[0]}'
                            self.task_dict[key] = func[1]
                        
task_list = TaskCollection()
__all__ = ["task_list"]