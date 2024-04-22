from fastapi import FastAPI
from postgres import connect, disconnect

from contextlib import asynccontextmanager
from params.router import router as router_reception


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


app.include_router(router_reception)
