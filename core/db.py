from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.settings import DatabaseSettings


def get_engine(settings: DatabaseSettings):
    return create_engine(settings.url)


def get_session(settings: DatabaseSettings) -> Session:
    return Session(get_engine(settings))
