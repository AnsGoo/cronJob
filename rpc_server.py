import zerorpc
from apscheduler.events import EVENT_JOB_MISSED,EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from scheduler.schedulers.gevent import ExtendGeventcheduler
from job.listener import CornJobListener
from app.common.logger import logger
from app.config import settings
from rpc import SchedulerService
from app.config import settings


config = settings.SCHEDULER_CONFIG
scheduler = ExtendGeventcheduler(
    jobstores=config.stores, 
    executors=config.executors, 
    job_defaults=config.default
)
listener = CornJobListener(schedule=scheduler).job_listener
scheduler.add_listener(listener,EVENT_JOB_EXECUTED|EVENT_JOB_ERROR|EVENT_JOB_MISSED)
scheduler.start()
try:
    logger.info('schduler has been started')
    server = zerorpc.Server(SchedulerService(scheduler=scheduler),pool_size=settings.RPC_POOL_SIZE)
    server.bind(settings.RPC_URL)
    logger.info('RPC server is run at %s' %settings.RPC_URL)
    server.run()
except KeyboardInterrupt:
    server.stop()
    logger.warning('stop RPC Server')
