from flask import g
import operator as op
import pandas as pd

# SHEET_PATH = "F:\drive\skami\sampla\python\public_comment\Full Council 2020-07-06.xlsx"

# data = pd.read_excel(SHEET_PATH, header=2)
# row = data.sample(1)

print()

class VoxPopuli:
    def __init__(self):
        self._table = None

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, obj):
        if isinstance(obj, dict):
            sheet = obj.get('sheet')
            header = obj.get('header', 0)

        self._table = self.read_xlsx(sheet, header)

    def get_row(self, table:pd.DataFrame=None, index:int=None) -> pd.Series:
        row = None
        df = self.table
        if df is not None:
            if index:
                row = df.iloc[index]
            else:
                unaccounted_df = self._filter_df(df, filters=['entered by'], func='isna')
                if unaccounted_df.empty:
                    unaccounted_df = df
                row = unaccounted_df.sample(1).iloc[0]

        return row

    @staticmethod
    def read_xlsx(file, header:int=0) -> pd.DataFrame:
        return pd.read_excel(file, header=int(header))

    @staticmethod
    def _filter_df(df, filters:dict, exclude=False, func='isin'):
        """
        """

        funcs = {
            'isin': pd.Series.isin,
            'df_isin': pd.DataFrame.isin,
            'isna': pd.Series.isna,
            'df_isna': pd.DataFrame.isna,
            'notna': pd.Series.notna,
            'df_notna': pd.DataFrame.notna
        }

        vert = op.inv if exclude or 'not ' in str(func) else op.pos
        func = funcs.get(func, func)

        if isinstance(filters, dict):
            for col, val in filters.items():
                if is_iter(col):
                    col = list(col)
                    func = funcs(f"df_{func.__name__}", func)
                df = df[vert(func(df[col], val)).any(axis='columns')]
        elif hasattr(filters, "__iter__"):
            for col in filters:
                if is_iter(col):
                    col = list(col)
                    func = funcs(f"df_{func.__name__}", func)
                df = df[vert(func(df[col]))]

        return df

def is_iter(obj) -> bool:
    return hasattr(obj, '__iter__') and not isinstance(obj, str)
