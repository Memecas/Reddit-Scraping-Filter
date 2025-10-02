
import pandas as pd
import re
from langdetect import detect, DetectorFactory

# Ensure reproducibility of language detection
DetectorFactory.seed = 0

def filter_non_english(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Filters a DataFrame to retain only entries where the specified text_column is detected as English.

    Preconditions:
    - `df` must be a Pandas DataFrame containing the `text_column`.

    Postconditions:
    - Returns a DataFrame containing only entries where the text is detected as English.

    Invariants:
    - The original DataFrame is not modified.
    """
    if text_column not in df.columns:
        print(f"Warning: \'{text_column}\' column not found. Skipping non-English filtering.")
        return df

    def is_english(text):
        if pd.isna(text) or not text.strip():
            return False
        try:
            return detect(text) == 'en'
        except:
            return False

    mask = df[text_column].apply(is_english)
    return df[mask].copy()

def filter_idioms(df: pd.DataFrame, text_column: str, idioms_list: list[str]) -> pd.DataFrame:
    """
    Filters a DataFrame to remove entries containing specified idioms.

    Preconditions:
    - `df` must be a Pandas DataFrame containing the `text_column`.
    - `idioms_list` must be a list of strings representing idioms to filter out.

    Postconditions:
    - Returns a DataFrame with entries containing specified idioms removed.

    Invariants:
    - The original DataFrame is not modified.
    """
    if text_column not in df.columns:
        print(f"Warning: \'{text_column}\' column not found. Skipping idiom filtering.")
        return df

    if not idioms_list:
        return df

    # Create a regex pattern to match any of the idioms, case-insensitive, whole word match
    idioms_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(idiom) for idiom in idioms_list) + r')\b', re.IGNORECASE)

    mask = df[text_column].fillna("").apply(lambda x: bool(idioms_pattern.search(x)))
    return df[~mask].copy()

def filter_min_word_count(comments_df: pd.DataFrame, min_words: int = 10) -> pd.DataFrame:
    """
    Filters comments DataFrame to retain only comments with at least `min_words`.
    This applies only to comments, as clarified by the user.

    Preconditions:
    - `comments_df` must be a Pandas DataFrame containing a 'body' column.
    - `min_words` must be an integer.

    Postconditions:
    - Returns a DataFrame containing only comments with word count >= `min_words`.

    Invariants:
    - The original DataFrame is not modified.
    """
    if 'body' not in comments_df.columns:
        print("Warning: 'body' column not found. Skipping min word count filtering.")
        return comments_df

    # Count words by splitting on whitespace
    comments_df['word_count'] = comments_df['body'].fillna('').apply(lambda x: len(x.split()))
    filtered_df = comments_df[comments_df['word_count'] >= min_words].copy()
    return filtered_df.drop(columns=['word_count'])


