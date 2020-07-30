import unittest
import sys
sys.path.append(".")
sys.path.append("./celery_queue")
import pytest
from unittest.mock import patch
from unittest import TestCase
import


@pytest.fixture(scope='session')
def db_engine(request):
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    db_url = request.config.getoption("--dburl")
    engine_ = create_engine(db_url, echo=True)

    yield engine_

    engine_.dispose()


@pytest.fixture(scope='session')
def db_session_factory(db_engine):
    """returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=engine))


@pytest.fixture(scope='function')
def db_session(db_session_factory):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    session_ = session_factory()

    yield session_

    session_.rollback()
    session_.close()

class TestQuery1(unittest.TestCase):

    def test_task_state_and_addition(self):

        task = tasks.add.apply(args=[3, 5])
        self.assertEqual(task.status, "SUCCESS")
        self.assertEqual(task.result, 8)


if __name__ == '__main__':
    unittest.main()