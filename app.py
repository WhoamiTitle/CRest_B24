from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


from bitrix24_crest import settings
from check_server import check_settings
from logging_module.logging_utility import log
from logging_module.schemes import LogMessage, log_en
from bitrix24_crest.bitrixcrest import BitrixCrest
from tests.test_data import add_test_contacts
import datetime


check_settings()


async def lifespan(app: FastAPI):
    start_time = datetime.datetime.now().isoformat()
    log(LogMessage(
        time=start_time,
        heder="Сервер запущен.",
        heder_dict={"event": "startup", "timestamp": start_time},
        body={"message": "FastAPI сервер успешно запущен."},
        level=log_en.INFO
    ))
    yield
    stop_time = datetime.datetime.now().isoformat()
    log(LogMessage(
        time=stop_time,
        heder="Сервер остановлен.",
        heder_dict={"event": "shutdown", "timestamp": stop_time},
        body={"message": "FastAPI сервер успешно остановлен."},
        level=log_en.INFO
    ))

app = FastAPI(lifespan=lifespan)

@app.exception_handler(Exception)
async def exception_handler(request: Request, error: Exception):
    log(LogMessage(
        time=None,
        heder="Неизвестная ошибка.",
        heder_dict=error.args,
        body={
            "url": str(request.url),
            "query_params": request.query_params._list,
            "path_params": request.path_params,
        },
        level=log_en.ERROR
    ))


print("BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter()


@router.head("/install")
async def init_head():
    pass


@router.head("/index")
async def index_head():
    pass


@router.post("/install", response_class=HTMLResponse)
async def install_post(DOMAIN: str, PROTOCOL: int, LANG: str, APP_SID: str, request: Request):
    auth_dict = await request.json()
    
    bitrix = BitrixCrest()
    bitrix.set_app_settings({
        "access_token": auth_dict["AUTH_ID"],
        "expires_in": auth_dict["AUTH_EXPIRES"],
        "refresh_token": auth_dict["REFRESH_ID"],
        "client_endpoint": f"https://{DOMAIN}/rest/",
        "member_id": auth_dict["member_id"],
        "application_token": APP_SID,
        "placement_options": auth_dict["PLACEMENT_OPTIONS"]
    })


    log(LogMessage(
        time=None,
        heder="Install.",
        heder_dict={},
        body={
            "DOMAIN": DOMAIN,
            "PROTOCOL": PROTOCOL,
            "LANG": LANG,
            "APP_SID": APP_SID,
            "auth_dict": auth_dict
        },
        level=log_en.DEBUG
    ))

    return """
    <head>
        <script src="//api.bitrix24.com/api/v1/"></script>
        <script>
            BX24.init(function(){
                BX24.installFinish();
            });
        </script>
    </head>
    <body>
            installation has been finished.
    </body>
    """



@router.post("/index", response_class=HTMLResponse)
async def index_post(DOMAIN: str, PROTOCOL: int, LANG: str, APP_SID: str, request: Request):
    auth_dict = await request.json()

    log(LogMessage(
        time=None,
        heder="Init.",
        heder_dict={},
        body={
            "DOMAIN": DOMAIN,
            "PROTOCOL": PROTOCOL,
            "LANG": LANG,
            "APP_SID": APP_SID,
            "auth_dict": auth_dict
        },
        level=log_en.DEBUG
    ))

    bitrix = BitrixCrest()
    results = await add_test_contacts(bitrix)
    print(results)
    return """
    <head>
        <script src="//api.bitrix24.com/api/v1/"></script>
        <script>
            BX24.init(function(){
                BX24.installFinish();
            });
        </script>
    </head>
    <body>
            installation has been finished.
    </body>
    """

app.include_router(router, tags=["webhook"])