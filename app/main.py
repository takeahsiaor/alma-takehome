from fastapi import FastAPI
from app import models, database
from app.routes import public, internal

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(public.router, prefix="/public", tags=["public"])
app.include_router(internal.router, prefix="/internal", tags=["internal"])

@app.get("/")
async def root():
    return {"message": "Hello home"}
