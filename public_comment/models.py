import pandas as pd

class Model:
    __slots__ = ['id', 'val']
    synonyms = {}

    def __init__(self, **kwargs):
        for slot in self.__slots__:
            setattr(self, slot, None)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def init(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.__slots__:
                val = self._coerce_type(val)
                setattr(self, key, val)

        self._fill_columns()
    
    def _fill_columns(self):
        for key, val in self.synonyms.items():
            if self[key]:
                setattr(self, val, self[key])
            elif self[val]:
                setattr(self, key, self[val])

    @staticmethod
    def _validate_attr(attr:str) -> str:
        """
        Returns a valid attribute as a string.
        """

        valid_attr = attr.replace(" ", "_")

        return valid_attr

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

            if val == "True":
                val = True
            elif val == "False":
                val = False

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
        new_obj = cls.from_dict(row.to_dict())

        return new_obj

    def to_list(self) -> list:
        return [getattr(self, val) for val in self.__slots__]

    @classmethod
    def from_dict(cls, dct):
        new_obj = cls()

        for slot in cls.__slots__:
            val = cls._coerce_type(dct.get(slot, None))
            if val:
                setattr(new_obj, cls._validate_attr(slot), val)

        new_obj.init(**dct)

        return new_obj

    def to_dict(self, flat=False):
        """
        Returns Model instance as a dictionary.
        If `flat`, nested dictionaries are 'hoisted' to the base level.
        """

        new_dict = {key: self.dictify(self[key]) for key in self.__slots__}

        if flat:
            new_dict = self._flatten(new_dict)

        return new_dict

    @staticmethod
    def _flatten(dct:dict) -> dict:
        new_dict = {}
        for key, val in dct.items():
            if isinstance(val, dict):
                for key, val in Model._flatten(val).items():
                    new_dict[key] = val
            new_dict[key] = val

        return new_dict

    @staticmethod
    def dictify(obj):
        """
        Returns a dictionary if `obj` is a `Model` instance.
        """

        try:
            obj = obj.to_dict()
        except AttributeError:
            pass

        return obj

    def __repr__(self):
        name = type(self).__name__
        return "{name}: {id} {val}".format(name=name, id=self[name.lower()+"_id"], val=self[name.lower()+"_val"])

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except TypeError:
            raise KeyError

class User(Model):
    __slots__ = ['user_id', 'user_val', 'name', 'username', 'password']
    synonyms = {'user_val': 'username'}

class Comment(Model):
    __slots__ = ['directory', 'track', 'entered_by', 'caller', 'location', 'sentiment', 'text', 'notes']

    def __init__(self):
        super().__init__()
        self.directory = ''
        self.track = 0
        self.entered_by = None
        self.caller = None
        self.location = None
        self.sentiment = None
        self.text = None

    @classmethod
    def from_dict(cls, dct):
        new_comment = super().from_dict(dct)
        new_comment.location = Location.from_dict(dct)
        new_comment.sentiment = Sentiment.from_dict(dct)

        new_comment.text = dct.get('edited text')
        if pd.isna(new_comment.text):
            new_comment.text = dct.get('full text')

        return new_comment

    def __repr__(self): return f"{self.directory}-{self.track} {self.caller}"

class Location(Model):
    __slots__ = ['district', 'neighborhood', 'street', 'city', 'zip', 'zone', 'npu', 'Atlanta', 'other_location']

class NPU(Model):
    __slots__ = ['npu_id', 'npu_val', 'name', 'neighborhoods']
    synonyms = {'npu_val': 'name'}

class Zone(Model):
    __slots__ = ['zone_id', 'zone_val', 'neighborhoods']

class Neighborhood(Model):
    __slots__ = ['neighborhood_id', 'neighborhood_val', 'name', 'npu', 'zone']
    synonyms = {'neighborhood_val': 'name'}

    def init(self, **kwargs):
        super().init(**kwargs)
        self.npu = NPU.from_dict(kwargs)
        self.zone = Zone.from_dict(kwargs)

class District(Model):
    __slots__ = ['district_id', 'district_val', 'councilor']

class Sentiment(Model):
    __slots__ = ['topic', 'intent']

    def __repr__(self): return f"{self.topic}: {self.intent}"
