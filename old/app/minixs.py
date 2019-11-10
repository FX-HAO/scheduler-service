from sqlalchemy.inspection import inspect

from . import db


class CRUDMixin(object):
    """Implements methods to create, read, update, and delete."""

    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_or_create(cls, id, commit=True, **kwargs):
        obj = cls.query.get(id) or cls(id)
        obj.update(commit=False, **kwargs)
        return obj.save(commit=commit)

    @classmethod
    def _filter(cls, **kwargs):
        query = cls.query
        for key, value in kwargs.iteritems():
            query = query.filter_by(**{key: value})
        return query.first()

    @classmethod
    def filter_or_create(cls, commit=True, **kwargs):
        self = cls._filter(**kwargs)
        if not self:
            self = cls.create(commit, **kwargs)
        return self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self


class Serializer(object):

    serialized_fields = ()

    def json(self):

        serialized_fields = self.serialized_fields
        cls_serialized_fields = set([column.name for column in
                                     self.__class__.__table__.columns])

        for primary_key in inspect(self.__class__).primary_key:
            if not getattr(self, primary_key.name):
                raise ValueError("The object hasn't been loaded yet.")

        if serialized_fields:
            for field in serialized_fields:
                if field not in cls_serialized_fields:
                    raise ValueError(
                        "The field `%s` isn't in `%s`"
                        % (field, self.__class__.__name__)
                    )
        else:
            serialized_fields = cls_serialized_fields
        ret = {}
        for field in serialized_fields:
            try:
                ret[field] = str(getattr(self, field))
            except UnicodeEncodeError as e:
                ret[field] = getattr(self, field)
        return ret
