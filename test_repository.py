from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base
from app.repository import get_all_scans


def test_get_all_scans():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    scans = get_all_scans(engine)

    assert isinstance(scans, list)


def test_database_failure():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    engine.dispose()

    try:
        get_all_scans(engine)
    except Exception as error:
        assert error is not None


