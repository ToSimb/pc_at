from fastapi import FastAPI
from contextlib import asynccontextmanager
from postgres import connect, disconnect

from params.router import router as router_params
from registration.router import router as router_registration

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

app.include_router(router_params)
app.include_router(router_registration)
