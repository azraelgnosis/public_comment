import click
from flask import current_app, Flask, g
from flask.cli import with_appcontext
import sqlite3


class Row(sqlite3.Row):
    def __init__(self, cursor, values):
        self.cursor = cursor
        self.values = values
        self.columns = [col[0] for col in cursor.description]
        self.val = " ".join([val for col, val in zip(self.columns, self.values) if 'val' in col]) # combines values with 'val in column name.

        for col, val in zip(self.columns, self.values):
            setattr(self, col, val)

    def get(self, attr:str):
        """
        Returns the value of `attr` if present
            else, returns None.
        """

        attribute = None
        try:
            attribute = getattr(self, attr)
        except AttributeError: pass

        return attribute

    def items(self):
        return zip(self.columns, self.values)

    def __getitem__(self, key:str):
        try:
            return getattr(self, key)
        except AttributeError:
            raise ValueError

    def __repr__(self): return f"{self.val}"


class DataManager:
    @staticmethod
    def get_db() -> sqlite3.Connection:
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = Row
        
        return g.db

    #TODO: somehow connect joining on the same table multiples times to the select columns
    @staticmethod
    def _join(from_table:str, join:dict) -> str:
        """
        Creates a left join clause for each table-column pair in `join`.
        """

        JOIN = ""
        if join:
            joins = []
            for idx, (table, on) in enumerate(join.items()):
                joins.append(f"LEFT JOIN {table} AS {table}{idx} ON {table}{idx}.{on} = {from_table}.{on}")
            
            JOIN = "\t\n".join(joins)

        return JOIN

    def get_columns(self, table:str) -> list:
        """
        Retrieves a list of `table` columns.

        :param table: Name of database table.
        :return: List of columns.
        """

        cursor = self.get_db().execute(f"SELECT * FROM {table} LIMIT 0")
        columns = [col[0] for col in cursor.description]

        return columns

    @staticmethod
    def _columns(columns) -> str:
        """
        If `columns` is a 
            str: returns unaltered.
            dict: joins table-column pairs as '`table`.column'.
            iterable: joins columns.
        """
        
        COLUMNS = ""
        if isinstance(columns, str):
            COLUMNS += columns
        elif isinstance(columns, dict):
            COLUMNS += ", ".join(f"`{table}`.{column}" for table, column in columns.items())
        elif hasattr(columns, "__iter__"):
            COLUMNS += ", ".join(columns)

        return COLUMNS

    @staticmethod
    def _where(conditions, pk='id', val='val') -> str:
        """
        """

        WHERE = ""
        try:
            WHERE += f"{pk} = {int(conditions)}"
        except ValueError:
            if isinstance(conditions, str):
                WHERE += f"{val} = '{conditions}'"

        return WHERE

    def select(self, table:str, columns='*', join=None, where=None, datatype=None) -> list:
        """
        SELECT `columns` FROM `table`
        """

        # SELECT = "SELECT {columns}".format(columns=self._columns(columns))
        # FROM = f"FROM {table}"
        # JOIN = self._join(table, join)
        # WHERE = f"WHERE {self._where(where)}" if where else ""

        SELECT = "SELECT {COLUMNS} FROM {TABLE} {JOIN} WHERE TRUE AND {WHERE}" \
            .format(
                COLUMNS=self._columns(columns),
                TABLE=table,
                JOIN=self._join(table, join),
                WHERE=self._where(where)
            )

        # results = self.get_db().execute(" ".join([SELECT, FROM, JOIN, WHERE])).fetchall()
        results = self.get_db().execute(SELECT).fetchall()
        if datatype:
            results = [datatype.from_row(result) for result in results]

        return results

    #TODO: columns parameter 
    #? and maybe intersection of table columns and values
    def insert(self, table:str, values:dict) -> None:
        """
        INSERT INTO `table` VALUES (`values`)
        """

        INSERT = f"INSERT INTO `{table}`"
        cols = self.get_columns(table)[1:]
        COLUMNS = "({})".format(", ".join(cols))
        VALUES = "VALUES ({})".format(", ".join("?" * len(cols)))

        db = self.get_db()
        db.execute(
            " ".join([INSERT, COLUMNS, VALUES]),
            [f"{values.get(key)}" for key in cols]
        )
        db.commit()

    # def __repr__(self): pass

    @staticmethod
    def init_db():
        db = DataManager.get_db()

        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))

    @staticmethod
    def init_app(app:Flask):
        app.teardown_appcontext(DataManager.close_db)
        app.cli.add_command(DataManager.init_db_command)
        
    @staticmethod
    def close_db(e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()

    @staticmethod
    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        """ Clear the existing data and create new tables."""

        DataManager().init_db()
        click.echo(f"Initialized the database.")

class Model:
    __slots__ = ['id', 'val']
    fks = {}

    def __init__(self):
        self.id = None
        self.val = None

    def init(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

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