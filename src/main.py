from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from postgres import connect, disconnect
from params.router import router as router_params
from registration.router import router as router_registration
from gui.router import router as router_gui
from join_scheme.router import router as router_join_scheme
from metric_info.router import router as router_metric_info
from check.router import router as router_check
from test.router import router as router_test

from logger.log_meddlewary import LogMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = connect()
    yield
    disconnect(app.state.pool)


def get_application() -> FastAPI:
    application = FastAPI(
        title="PC AT",
        lifespan=lifespan
    )
    return application


app = get_application() 
app.add_middleware(LogMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")



app.include_router(router_join_scheme)
app.include_router(router_registration)
app.include_router(router_check)
app.include_router(router_metric_info)
app.include_router(router_params)
app.include_router(router_gui)
app.include_router(router_test)
