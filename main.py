import sys
from pathlib import Path

sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/schemas/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/routers/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/validations/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/utils/")))

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.db import create_database
from routers.authentication.auth_routes import router as auth_router
from routers.authentication.roles_routes import router as roles_router
from routers.authentication.users_routes import router as users_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize or Connect Database
    await create_database()
    
    yield
    
    print("Shutting Down")


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def greet():
    return { 
        "Project": "Fin Tech App Backend",
        "Author": "asta",
        "Version": "1.0.4",
        "Description": "A Sand Box Application for Developers for Testing."
    }


app.include_router(auth_router, tags=["Authentication"])
app.include_router(roles_router, tags=["Roles"])
app.include_router(users_router, tags=["Users"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
