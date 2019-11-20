class CRUDMixin:

    def to_dict(self):
        fields = list(self.fields.keys())
        return dict((f, getattr(self, f)) for f in fields)
