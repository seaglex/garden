import datetime as dt
import contextlib
import unittest
import pdb
import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import MetaData, create_engine, Column, Integer, String, DateTime
from sqlalchemy import pool
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base


# DB_URL = "sqlite:///:memory:"
DB_URL = "mysql://root@localhost/test"
eng1 = create_engine(DB_URL, echo=True)
Base = declarative_base()
Session = orm.sessionmaker(bind=eng1, autoflush=True, autocommit=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(32))
    created_at = Column(DateTime)
    def __init__(self, id, user_name):
        self.id = id
        self.user_name = user_name
        self.created_at = dt.datetime.now()

class UpdateTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(eng1)

    def tearDown(self):
        Base.metadata.drop_all(eng1)

    def _update_rows(self, session_cls):
        with contextlib.closing(session_cls()) as ses:
            ses.add(User(1, "wx"))
            ses.add(User(2, "zh"))
            ses.commit()
        with contextlib.closing(session_cls()) as ses:
            users = ses.query(User).all()
            users = {u.id: u for u in users}
            users[1].user_name = "weixuan"
            user2 = users[2]
            ses.commit()
        user2.user_name = "zhenghua"

    def _show_results(self, session_cls):
        with contextlib.closing(session_cls()) as ses:
            query = ses.query(User)
            for u in query:
                print(u.id, u.user_name)

    def test(self):
        # pdb.set_trace()
        self._update_rows(Session)
        self._show_results(Session)

if __name__ == "__main__":
    unittest.main()