import orm
import sqlalchemy


metadata = sqlalchemy.MetaData()


def create_orm(databases_obj):
    orm.Model.__database__ = databases_obj
    return orm
