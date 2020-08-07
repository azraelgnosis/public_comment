from collections import defaultdict
import operator as op
import os
import pandas as pd
import sys

PATH = os.path.dirname(__file__)

KEYWORDS = ['abolish', 'defund', 'reform']
PUNCTUATION = [',', '.', '"', "'", '?', '!', '(', ')', ':', ';', '\n']
SENTIMENTS = ['defund', 'reform', 'abolish', 'support', 'prison', 'communities', 'education', 'healthcare', 'other']
sentiment_keywords = {
    'defund': ['defund', 'defunding', 'divest', 'allocate', 'allocation', 'reallocate', 'reallocation', 'funds', 'funding', 'budget'],
    'reform': ['reform', 'training'],
    'abolish': ['abolish', 'dismantle'],
    'support': ['blue'],
    'prison': ['prison', 'prison', 'jail', 'jails'],
    'communities': ['community', 'communities', 'social'],
    'education': ['education', 'school', 'schools', 'teacher', 'teachers', 'teaching'], 
    'healthcare': ['insurance', 'medical', 'healthcare', 'medicine', 'medication'],
    'other': []
}


class Analyzer:
    def __init__(self, file_path=None):
        self.file_path = self._verify_file_path(file_path)

        self.extension_functions = {
            '.csv': {
                'load': self.load_csv,
                'save': self.save_csv
            },
            '.xlsx': {
                'load': self.load_xlsx,
                'save': self.save_xlsx
            }
        }

    def _verify_file_path(self, file_path:str) -> str:
        """
        Checks if the file indicated by `file_path` exists and if not,
            prepends the current directory path.
        
        :param file_path: Path to file.
        :return: File path.
        """

        if not os.path.exists(file_path) and len(os.path.split(file_path) == 1):
            file_path = self._verify_file_path(os.path.join(PATH, file_path))
        elif not os.path.exists(file_path):
            raise FileExistsError

        return file_path

    def load_table(self) -> pd.DataFrame:
        """
        Loads the data in `self.file_path` into a DataFrame.
        """

        extension = os.path.splitext(self.file_path)[1]
        func = self.extension_functions[extension]['load']
        df = func(self.file_path)

        return df

    @staticmethod
    def load_xlsx(file_path:str) -> pd.DataFrame:
            return pd.read_excel(file_path)

    @staticmethod
    def load_csv(file_path:str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def save_table(self, data:pd.DataFrame, filename:str=None, file_extension:str=None) -> None:
        extension = file_extension or os.path.splitext(self.file_path)[1]
        func = self.extension_functions.get(extension)['save']
        func(data, filename)

    @staticmethod
    def save_xlsx(data:pd.DataFrame, filename:str="public comment") -> None:
            data.to_excel(".".join([filename, 'xlsx']))

    @staticmethod
    def save_csv() -> None:
        raise NotImplementedError

    @staticmethod
    def replace_many(text:str, subs:dict) -> str:
        """
        Replaces values in `text` with substitutes in `subs`.

        :param text: String to replace values in.
        :param subs: Dictionary containing values to replace.
        :return: Text with values replaced.
        """

        for old, new in subs.items():
            text = text.replace(old, new)

        return text

    @staticmethod
    def sanitize(text:str):
        """
        Removes extraneous characters (mostly punctuation) from `text`.

        :param text: Text to sanitized.
        :return: Sanitized text.
        """

        text = text.lower()
        punct_dict = {punc: "" for punc in PUNCTUATION}
        text = replace_many(text, punct_dict)

        return text

    def calc_level_0(self) -> None:
        """
        Selects unexamined transcripts and applies a naïve, low-level analysis of the sentiment based on mere mention of any of the sentiment's keywords.
        """

        data = self.load_table()
        # unanalyzed = self._filter_df(data, filters={'entered by'}, func='isna')
        unanalyzed = self._filter_df(data, filters={*SENTIMENTS}, func='isna')

        def lvl_0(row):
            transcript = row['full text']
            
            sentiment_mentions = pd.Series(["?" * len(SENTIMENTS)])
            if pd.notna(transcript):
                sentiment_mentions = [self.check_mention(sentiment, transcript) for sentiment in SENTIMENTS]

            return pd.Series(sentiment_mentions)

        analyzed = unanalyzed.copy()
        analyzed[SENTIMENTS] = unanalyzed.apply(lvl_0, axis=1)
        analyzed['entered by'] = 'lvl_0'

        updated_df = self._update_df(data, analyzed)

        self.save_table(updated_df, "public_comment_lvl0")

    def calc_level_1(self):
        data = self.load_table()
        # unanalyzed = self._filter_df(data, filters={'entered by'}, func='isna')
        unanalyzed = self._filter_df(data, filters={*SENTIMENTS}, func='isna')

        def lvl_1(row):
            transcript = row['full text']

            sentiment_mentions = pd.Series(["?" * len(SENTIMENTS)])
            for sentiment in SENTIMENTS:
                self.get_mention_context(sentiment, transcript)
                raise NotImplementedError

        analyzed = unanalyzed.copy()
        analyzed[SENTIMENTS] = unanalyzed.apply(lvl_1, axis=1)
        analyzed['entered by'] = 'lvl1'
        updated_df = self._update_df(data, analyzed)

        self.save_table(updated_df, "public_comment_lvl1")

    @staticmethod
    def check_mention(sentiment:str, transcript:str) -> bool:
        """
        Checks if any of the `sentiment`'s keywords are present in the `trascript`.
        """

        return any((keyword in transcript) for keyword in sentiment_keywords.get(sentiment))

    @staticmethod
    def get_mention_context(sentiment:str, transcript:str) -> str:
        """
        Hm...

        Checks if any of the `sentiment`'s keywords are present in the `transcript`.
        If so, the context is presented to the user to verify if the sentiment.
        """

        sentences = transcript.split(".")
        check = False
        for keyword in sentiment_keywords.get(sentiment):
            for sentence in sentences:
                if check:
                    break
                if keyword in sentence:
                    note = input(f"{keyword}? y/n \n {sentence}")
                    check = True if note == 'y' else False

        raise NotImplementedError

    @staticmethod
    def _update_df(anchor_df:pd.DataFrame, target_df:pd.DataFrame, index:str=None) -> pd.DataFrame:
        """
        Updates `anchor_df` with the values in `target_df` based on their index or after resetting their indices if provided.

        :param anchor_df: DataFrame to be updated.
        :param target_df: DataFrame with updated values.
        :param index: Column to align both DataFrames on.
        :return: Updated DataFrame.
        """

        if index:
            anchor_df.reset_index(index, inplace=True)
            target_df.reset_index(index, inplace=True)

        anchor_df.update(target_df)

        if index:
            anchor_df.reset_index()

        return anchor_df


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = 'public comment.xlsx'
    analyzer = Analyzer(filename)
    analyzer.calc_level_0()
    # analyzer.calc_level_1()
    print("done")
