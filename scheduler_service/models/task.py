from datetime import datetime

from motorengine import (Document, URLField, ListField, JsonField, DateTimeField, EmbeddedDocumentField, StringField)


class Response(Document):
    time = DateTimeField(default=datetime.now)
    response = JsonField()


class URLDetail(Document):
    name = StringField(max_length=32, required=True)
    url = URLField()
    responses = ListField(EmbeddedDocumentField(embedded_document_type=Response))

class Task(Document):
    __collection__ = 'task'

    urls = ListField(EmbeddedDocumentField(URLDetail))

