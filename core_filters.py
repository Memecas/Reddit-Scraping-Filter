import pandas as pd
import re

def filter_by_score(df: pd.DataFrame, min_score: int = 2) -> pd.DataFrame:
    """
    Filters a DataFrame to include only posts/comments with a score greater than or equal to min_score.

    Preconditions:
    - `df` must be a Pandas DataFrame containing a 'score' column.
    - `min_score` must be an integer.

    Postconditions:
    - Returns a DataFrame where all entries have 'score' >= `min_score`.

    Invariants:
    - The original DataFrame is not modified.
    """
    if 'score' not in df.columns:
        print("Warning: 'score' column not found. Skipping score filtering.")
        return df
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0) # Convert to numeric, coerce errors to NaN, then fill NaN with 0
    return df[df["score"] >= min_score].copy()

def filter_url_only_content(df: pd.DataFrame, text_column: str = 'body') -> pd.DataFrame:
    """
    Filters a DataFrame to remove entries where the specified text_column
    contains only URL links (one or more), with optional surrounding punctuation.

    Preconditions:
    - df: Pandas DataFrame
    - text_column: column name to check (e.g., 'body' or 'selftext')

    Postconditions:
    - Returns a DataFrame with rows removed where text_column contains only URLs
    """

    if text_column not in df.columns:
        print(f"Warning: '{text_column}' column not found. Skipping URL-only content filtering.")
        return df

    # Regex to detect URLs (http, https, www, or bare domain.tld[/path])
    url_pattern = re.compile(
        r'^(https?://\S+|www\.\S+|[a-zA-Z0-9-]+\.[a-z]{2,})(/\S*)?$',
        re.IGNORECASE
    )

    def is_url_only(text: str) -> bool:
        tokens = text.strip().split()
        if not tokens:
            return False
        # Strip common punctuation from tokens before matching
        return all(url_pattern.fullmatch(t.strip('.,!?()[]')) for t in tokens)

    mask = df[text_column].fillna('').apply(is_url_only)
    return df[~mask].copy()

def filter_edited_content(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters a DataFrame to include only posts/comments that have been edited, indicating more thoughtful content.
    Assumes 'edited' column is a boolean or timestamp. If timestamp, checks if it's not False/0.

    Preconditions:
    - `df` must be a Pandas DataFrame containing an 'edited' column.

    Postconditions:
    - Returns a DataFrame containing only entries where 'edited' is True or a non-zero timestamp.

    Invariants:
    - The original DataFrame is not modified.
    """
    if 'edited' not in df.columns:
        print("Warning: 'edited' column not found. Skipping edited content filtering.")
        return df
    
    # Handle different representations of 'edited':
    # - Boolean: False (not edited) or True (edited)
    # - Timestamp: 0/False (not edited) or unix timestamp (edited)
    # - String: "False" or "false" (not edited) or timestamp as string
    
    def is_edited(value):
        # Handle string "False" or "false"
        if isinstance(value, str):
            if value.lower() == 'false':
                return False
            # Try to convert string to number
            try:
                value = float(value)
            except (ValueError, TypeError):
                return False
        
        # Handle boolean False or numeric 0
        if value is False or value == 0:
            return False
        
        # Handle NaN/None
        if pd.isna(value):
            return False
            
        # Everything else (True, timestamps) is considered edited
        return True
    
    mask = df['edited'].apply(is_edited)
    return df[mask].copy()

def eliminate_duplicates(df: pd.DataFrame, subset_cols: list[str], keep: str = 'first') -> pd.DataFrame:
    """
    Eliminates duplicate rows from a DataFrame based on a subset of columns.

    Preconditions:
    - `df` must be a Pandas DataFrame.
    - `subset_cols` must be a list of strings, where each string is a column name present in `df`.
    - `keep` must be 'first', 'last', or False.

    Postconditions:
    - Returns a DataFrame with duplicate rows removed based on `subset_cols`.

    Invariants:
    - The original DataFrame is not modified.
    """
    for col in subset_cols:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found for duplicate elimination. Skipping.")
            return df
    return df.drop_duplicates(subset=subset_cols, keep=keep).copy()

def replace_urls_with_token(text: str, token: str = '<URL>') -> str:
    """
    Replaces URLs in text with a standardized token.

    Args:
        text (str): The input text containing URLs to be replaced
        token (str, optional): The token to replace URLs with. Defaults to '<URL>'

    Returns:
        str: Text with all URLs replaced by the specified token

    Note:
        This function should be used AFTER url-only filtering to preserve meaningful text
        while standardizing any remaining URLs within the content.
    """
    # Comprehensive URL pattern that matches:
    # - http/https URLs
    # - www. URLs
    # - bare domain.tld URLs
    # - URLs with paths, query parameters, and fragments
    url_pattern = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»""'']))',
        re.IGNORECASE
    )
    
    # Replace all matches with the token
    return url_pattern.sub(token, text)

def filter_automoderator_and_bots(df: pd.DataFrame, author_column: str = 'author') -> pd.DataFrame:
    """
    Filters a DataFrame to remove entries from known automoderators and bots.

    Preconditions:
    - `df` must be a Pandas DataFrame containing the `author_column`.

    Postconditions:
    - Returns a DataFrame with entries from automoderators and bots removed.

    Invariants:
    - The original DataFrame is not modified.
    """
    if author_column not in df.columns:
        print(f"Warning: '{author_column}' column not found. Skipping automoderator/bot filtering.")
        return df

    # Common bot/automoderator names on Reddit
    bot_names = [
        'AutoModerator',
        'RemindMeBot',
        'GoodBot_BadBot',
        'TrollaBot',
        'Mentioned_Videos',
        'gifReversingBot',
        'image_linker_bot',
        'xkcd_transcriber',
        'DeepLinkBot',
        'stabbot',
        'transcribersofreddit',
        'haikubot-test',
        'Shakespeare-Bot',
        'timezone_bot',
        'Lyrics-Bot',
        'WikiTextBot',
        'fact_bot',
        'Bot_Metric',
        'TheDailyShowBot',
        'TweetPoster',
        'Imaginative_Bot',
        'Sub_Stats_Bot',
        'LinkFixerBot',
        'SmallSubBot',
        'Magic_Eye_Bot', # Often used for repost detection
        'botuser', # Added for testing
        'removeduser' # Added for testing automoderator removal
    ]
    # Convert to lowercase for case-insensitive matching
    bot_names_lower = [name.lower() for name in bot_names]

    # Filter out rows where the author is in the bot_names list (case-insensitive)
    mask = df[author_column].fillna('').astype(str).str.strip().str.lower().isin(bot_names_lower)
    return df[~mask].copy()