from schemas import *
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(bind=engine,
                                       expire_on_commit=False,
                                       class_=AsyncSession)


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            
        except SQLAlchemyError:
            await session.rollback()
            raise
        
        finally:
            await session.close()


# Database Table Creation Util
async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database Created Successfully.")


# Database Dependency Injection for Routes
db_dependency = Annotated[AsyncSession, Depends(get_db)]