
import pandas as pd

def load_comments_from_csv(file_path: str) -> pd.DataFrame:
    """
    Loads Reddit comments from a CSV file into a Pandas DataFrame.

    Preconditions:
    - `file_path` must be a valid path to a CSV file.
    - The CSV file must contain columns relevant to Reddit comments (e.g., 'body', 'score', 'author', 'created_utc').

    Postconditions:
    - Returns a Pandas DataFrame containing the comment data.
    - The DataFrame will have at least the expected columns.

    Invariants:
    - The input CSV file is not modified.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: Comment file not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading comment data from {file_path}: {e}")
        return pd.DataFrame()

def load_submissions_from_csv(file_path: str) -> pd.DataFrame:
    """
    Loads Reddit submissions from a CSV file into a Pandas DataFrame.

    Preconditions:
    - `file_path` must be a valid path to a CSV file.
    - The CSV file must contain columns relevant to Reddit submissions (e.g., 'title', 'selftext', 'score', 'author', 'created_utc').

    Postconditions:
    - Returns a Pandas DataFrame containing the submission data.
    - The DataFrame will have at least the expected columns.

    Invariants:
    - The input CSV file is not modified.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: Submission file not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading submission data from {file_path}: {e}")
        return pd.DataFrame()



