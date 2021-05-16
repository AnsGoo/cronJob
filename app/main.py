
import os
import fcntl
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .route import router
from app.config import settings
from app.common.logger import logger
from .database import create_table

from scheduler.schedulers.asyncio import ExtendAsyncIOScheduler
from apscheduler.events import EVENT_JOB_MISSED,EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from job.listener import CornJobListener
from app.state import default_state


def get_application():
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description='一款轻量级定时任务调度平台'
    )

    register_cors(_app)

    # 注册路由
    register_router(_app)

    # 请求拦截
    register_hook(_app)

    # 注册任务调度
    register_scheduler(_app)


    return _app


def register_router(app: FastAPI) -> None:
    """
    注册路由
    这里暂时把两个API服务写到一起，后面在拆分
    :param app:
    :return:
    """
    # 项目API
    app.include_router(router)


def register_cors(app: FastAPI) -> None:
    """
    支持跨域
    :param app:
    :return:
    """
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )



def register_hook(app: FastAPI) -> None:
    """
    请求响应拦截 hook
    https://fastapi.tiangolo.com/tutorial/middleware/
    :param app:
    :return:
    """

    @app.middleware("http")
    async def logger_request(request: Request, call_next) -> Response:
        # https://stackoverflow.com/questions/60098005/fastapi-starlette-get-client-real-ip
        # logger.info(f"访问记录:{request.method} url:{request.url}\nheaders:{request.headers}\nIP:{request.client.host}")
        response = await call_next(request)
        return response

def register_scheduler(app: FastAPI) -> None:
    """
    注册任务调度对象
    :param app:
    :return:
    """
    f = open("scheduler.lock", "wb")
    @app.on_event("startup")
    async def load_schedule_or_create_blank():
        config = settings.SCHEDULER_CONFIG
        schedule = ExtendAsyncIOScheduler(
            jobstores=config.stores, 
            executors=config.executors, 
            job_defaults=config.default
        )
        if os.name == 'posix':
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                lister = CornJobListener(schedule=schedule).job_lister
                schedule.add_listener(lister,EVENT_JOB_EXECUTED|EVENT_JOB_ERROR|EVENT_JOB_MISSED)
                schedule.start()
                default_state.schedule = schedule
            except BlockingIOError:
                pass
        else:
            schedule.start()
            default_state.schedule.schedule = schedule

        logger.info("start Schedule Object")

    @app.on_event('shutdown')
    async def shutdown_schedule():
        """
        关闭调度对象
        :return:
        """
        if os.name == 'posix':
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
            default_state.schedule.schedule.shutdown()
        else:
            app.state.schedule.shutdown()
        logger.warning("Schedule shutdown")

app = get_application()

create_table()
