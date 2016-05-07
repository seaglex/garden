import datetime as dt
import pdb
import threading
import time

import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import MetaData, create_engine, Column, Integer, String, DateTime
from sqlalchemy import pool
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

# DB_URL = "sqlite:///:memory:"
DB_URL = "mysql://root@localhost/test"
eng1 = create_engine(DB_URL)
eng2 = create_engine(DB_URL, poolclass=pool.NullPool)
Base = declarative_base()
Session = orm.sessionmaker(bind=eng1, autoflush=True, autocommit=False)

class Users(Base):
    __tablename__ = "test_lock_users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(32))
    created_at = Column(DateTime)
    def __init__(self, id, user_name):
        self.id = id
        self.user_name = user_name
        self.created_at = dt.datetime.now()

def query_and_sleep(is_commit_session, is_closing_session):
    prefix = "\tthread:"
    ses = Session()
    ses.add(Users(1, "admin"))
    ses.add(Users(2, "guest"))
    users = ses.query(Users)
    # It's important to print users.count(), or no table lock at all
    print(prefix, "add and query table - there are {0} items".format(users.count()))
    if is_commit_session:
        ses.commit()
        print(prefix, "commit session")
    if is_closing_session:
        ses.close()
        print(prefix, "close session")
    for n in range(6):
        time.sleep(0.1)
        print(prefix, ".")
    if not is_commit_session:
        ses.commit()
        print(prefix, "commit session")
    if not is_closing_session:
        ses.close()
        print(prefix, "close session")

def test_update_table(is_commit_session, is_closing_session):
    with eng2.connect() as conn:
        conn.execute("drop table if exists {0};".format(Users.__tablename__))
    Base.metadata.create_all(eng2)

    print("start query thread")
    thread = threading.Thread(target=lambda: query_and_sleep(is_commit_session, is_closing_session))
    thread.start()

    time.sleep(0.1)
    print("try alter table")
    with eng2.connect() as conn:
        conn.execute("alter table {0} modify column user_name varchar(64) default null".format(Users.__tablename__))
        print("Succeed to alter table")

    thread.join()
    with eng2.connect() as conn:
        conn.execute("drop table {0};".format(Users.__tablename__))
    return

if __name__ == "__main__":
    # pdb.set_trace()
    print("test: commit and close later")
    test_update_table(False, False)
    print()
    print("test: commit immediately and close later")
    test_update_table(True, False)
    print()
    print("test: commit and close immediately ")
    test_update_table(True, True)
    print()
