from mongoengine import Document, StringField


class Subject(Document):
    emoji = StringField(required=True, max_length=5)
    name = StringField(required=True, max_length=55, unique_with='emoji')
    url = StringField(required=True, max_length=120, unique=True)

    def __str__(self):
        return f"{self.header} {self.url}"

    @property
    def header(self):
        return f"{self.emoji} {self.name}"
