class Model:
    __slots__ = ['id', 'val']
    synonyms = {}

    def __init__(self):
        self.id = None
        self.val = None

    def init(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

        self._fill_columns()
    
    def _fill_columns(self):
        for key, val in self.synonyms.items():
            if self[key]:
                setattr(self, val, self[key])
            elif self[val]:
                setattr(self, key, self[val])

    @staticmethod
    def _coerce_type(val, separator=","):
        """
        Coerces `val` as a float or int if applicable,
        else returns original value.

        :param val: Value to coerce.
        """

        if isinstance(val, str):
            if len(coll := val.split(separator)) > 1:
                val = [Model._coerce_type(elem.strip()) for elem in coll]

            try:
                if "." in str(val):
                    val = float(val)
                else:
                    val = int(val)
            except TypeError: pass
            except ValueError: pass

        return val

    @classmethod
    def from_row(cls, row):
        new_obj = cls()

        for col in row.columns:
            setattr(new_obj, col, row.get(col))

        new_obj.init()

        return new_obj

    def to_list(self) -> list:
        return [getattr(self, val) for val in self.__slots__]

    @classmethod
    def from_dict(cls, dct):
        new_obj = cls()

        for slot in cls.__slots__:
            val = cls._coerce_type(dct.get(slot))
            setattr(new_obj, slot, val)

        new_obj.init()

        return new_obj

    def to_dict(self):
        return {key: getattr(self, key) for key in self.__slots__}

    def __repr__(self):
        name = type(self).__name__.lower()
        return "{name}: {id} {val}".format(name=name, id=self[name+"_id"], val=self[name+"_val"])

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except TypeError:
            raise KeyError

class User(Model):
    __slots__ = ['name', 'val', 'username', 'password']
    synonyms = {'val': 'username'}