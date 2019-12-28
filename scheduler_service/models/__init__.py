import databases
import orm
import sqlalchemy

metadata = sqlalchemy.MetaData()


def create_orm(database_obj: databases.Database):
    engine = sqlalchemy.create_engine(str(database_obj.url))
    metadata.create_all(engine)

    orm.Model.__database__ = database_obj
    orm.Model.__metadata__ = metadata
    return orm.Model


from .user import User

__all__ = [
    'User'
]