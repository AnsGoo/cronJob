
from apscheduler.job import Job
from apscheduler.events import JobEvent

class JobBaseListener:

    def __init__(self, schedule) -> None:
        self.schedule = schedule

    
    def save_record(self,event: JobEvent, job: Job) -> None:
        pass

    def job_listener(event: JobEvent) -> None:
        pass