from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from check_server import check_settings

check_settings()

app = FastAPI()


@app.head("/install")
async def init_head():
    pass


@app.head("/index")
async def index_head():
    pass


@app.post("/install", response_class=HTMLResponse)
async def install_post():
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



@app.post("/index", response_class=HTMLResponse)
async def index_post():
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
