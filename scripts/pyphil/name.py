
class Name:

    @classmethod
    def of(cls, name):
        return Name(name)

    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name
