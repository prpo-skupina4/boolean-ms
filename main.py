from fastapi import FastAPI
import api
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FRITIME Boolean Service")

app.include_router(api.router, prefix="/bool")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
