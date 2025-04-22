import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.db import create_database

import sys
from pathlib import Path

sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/schemas/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/routers/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/validations/")))
sys.path.insert(0, str(Path.joinpath(Path.cwd().absolute(), "/utils/")))


from routers.subscription.subscriptions_routes import router as subscription_router
from routers.authentication.users_routes import router as users_router
from routers.authentication.roles_routes import router as roles_router
from routers.authentication.auth_routes import router as auth_router
from routers.product.products_routes import router as product_router
from routers.subscription.payments_routes import router as payment_router
from routers.account.accounts_routes import router as accounts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize or Connect Database
    await create_database()

    yield

    print("Shutting Down")


app = FastAPI(lifespan=lifespan)


# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def greet():
    return {
        "Project": "Fin Tech App Backend",
        "Author": "asta",
        "Version": "1.0.5",
        "Description": "A Sand Box Application for Developers for Testing."
    }


app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(roles_router, prefix="/api", tags=["Roles"])
app.include_router(users_router, prefix="/api", tags=["Users"])
app.include_router(product_router, prefix="/api", tags=["Products"])
app.include_router(payment_router, prefix="/api", tags=["Payments"])
app.include_router(subscription_router, prefix="/api", tags=["Subscriptions"])
app.include_router(accounts_router, prefix="/api", tags=["Accounts"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
