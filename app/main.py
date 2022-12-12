
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .route import router
from app.config import settings
from .database import create_table


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
    @app.on_event("startup")
    async def load_schedule_or_create_blank():
        create_table()

    @app.on_event('shutdown')
    async def shutdown_schedule():
        """
        关闭调度对象
        :return:
        """
        pass

app = get_application()


