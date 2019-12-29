# from datetime import datetime

# from motorengine import (Document, URLField, ListField, JsonField,
#     DateTimeField, EmbeddedDocumentField, StringField, IntField)


# class Response(Document):
#     time = DateTimeField(default=datetime.now)
#     response = JsonField()


# class URLDetail(Document):
#     name = StringField(max_length=32, required=True)
#     request_url = URLField()
#     callbasck_url = URLField()
#     responses = ListField(EmbeddedDocumentField(embedded_document_type=Response))

# class Task(Document):
#     __collection__ = 'task'
#
#     name = StringField(required=True)
#     user_id = IntField(required=True)
#     interval_time = IntField(required=True)
#     urls = ListField(EmbeddedDocumentField(URLDetail))

