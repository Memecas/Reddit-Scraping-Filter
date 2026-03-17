
import pandas as pd
import re
from langdetect import detect, DetectorFactory

# Ensure reproducibility of language detection
DetectorFactory.seed = 0

def filter_non_english(df: pd.DataFrame, text_column: str, target_lang: str = 'en') -> pd.DataFrame:
    """
    Filters a DataFrame to retain only entries where the specified text_column is detected as the target language.

    Preconditions:
    - `df` must be a Pandas DataFrame containing the `text_column`.
    - `target_lang` must be a valid language code (e.g., 'en', 'es', 'fr').

    Postconditions:
    - Returns a DataFrame containing only entries where the text matches the target language.

    Invariants:
    - The original DataFrame is not modified.
    """
    if text_column not in df.columns:
        print(f"Warning: \'{text_column}\' column not found. Skipping language filtering.")
        return df

    def is_target_lang(text):
        if pd.isna(text) or not text.strip():
            return False
        try:
            return detect(text) == target_lang
        except:
            return False

    mask = df[text_column].apply(is_target_lang)
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

def filter_min_word_count(comments_df: pd.DataFrame, min_words: int = 10, text_column: str = 'body') -> pd.DataFrame:
    """
    Filters DataFrame to retain only entries with at least `min_words`.

    Preconditions:
    - `comments_df` must be a Pandas DataFrame containing the specified text_column.
    - `min_words` must be an integer.

    Postconditions:
    - Returns a DataFrame containing only entries with word count >= `min_words`.

    Invariants:
    - The original DataFrame is not modified.
    """
    if text_column not in comments_df.columns:
        print(f"Warning: '{text_column}' column not found. Skipping min word count filtering.")
        return comments_df

    # Count words by splitting on whitespace
    word_counts = comments_df[text_column].fillna('').apply(lambda x: len(x.split()))
    return comments_df[word_counts >= min_words].copy()


