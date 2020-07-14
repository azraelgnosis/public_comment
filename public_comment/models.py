from public_comment.db import Model

class User(Model):
    __slots__ = ['name', 'username', 'password']