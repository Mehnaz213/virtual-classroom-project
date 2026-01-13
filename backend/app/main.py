from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, classroom, events, reports, ws, labeler
from app.config import get_settings
from app.db import init_db, session


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from app.db.base_class import Base

        Base.metadata.create_all(bind=session.engine)
        with session.SessionLocal() as db:
            init_db.init_db(db)
        yield

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Focus Mate - AI-Powered Virtual Classroom with advanced attention detection and lock mode enforcement.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(classroom.router, prefix=settings.api_v1_prefix)
    app.include_router(events.router, prefix=settings.api_v1_prefix)
    app.include_router(reports.router, prefix=settings.api_v1_prefix)
    app.include_router(labeler.router, prefix=settings.api_v1_prefix)
    app.include_router(ws.router)

    return app


app = create_app()

