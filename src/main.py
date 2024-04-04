from fastapi import FastAPI

from reception.router import router as router_reception

app = FastAPI(
    title="PC AT"
)

app.include_router(router_reception)
