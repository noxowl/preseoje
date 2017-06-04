from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, DateTime

from preseoje.config import DATABASE_PATH

__all__ = ('session', 'Base', 'Schedules', 'initialize')

engine = create_engine(
    'sqlite:///{}'.format(DATABASE_PATH), convert_unicode=True, echo=True)
session = scoped_session(sessionmaker(autocommit=True,
                                        autoflush=True,
                                        bind=engine))

Base = declarative_base()
Base.query = session.query_property()


class Schedules(Base):
    __tablename__ = 'schedules'

    uid = Column(Integer, primary_key=True)
    datetime = Column(DateTime, unique=True)
    content = Column(String)

    __repr_columns__ = uid, datetime, content


def initialize():
    Base.metadata.create_all(bind=engine)
