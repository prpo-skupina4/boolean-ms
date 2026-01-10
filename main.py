from fastapi import FastAPI
import api

app = FastAPI(title="FRITIME Boolean Service")

app.include_router(api.router, prefix="/bool")
