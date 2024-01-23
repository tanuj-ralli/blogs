from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, blog

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(blog.router)
