import sys
from pathlib import Path


sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/schemas/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/routers/")))

import uvicorn
from fastapi import FastAPI
from routers.authentication.routes import router as auth_router


app = FastAPI()



@app.get('/')
async def greet():
    return { 
        "Project": "Fin Tech App Backend",
        "Author": "asta",
        "Version": "1.0.1",
        "Description": "A Sand Box Application for Developers for Testing."
    }


app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
