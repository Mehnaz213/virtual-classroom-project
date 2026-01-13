import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        init_db(db)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

