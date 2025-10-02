import pandas as pd
import hashlib
import re

def hash_username(username: str, salt: str = "your_secret_salt") -> str:
    """
    Hashes a username using SHA256 to anonymize while maintaining consistency.
    Same username will always produce the same hash.
    
    Args:
        username: The username to hash
        salt: A secret salt for additional security
    
    Returns:
        A hashed version of the username
    """
    if pd.isna(username) or username in ['[deleted]', '[removed]', '']:
        return username
    
    # Create hash of username + salt
    hash_object = hashlib.sha256(f"{username}{salt}".encode())
    return f"user_{hash_object.hexdigest()[:16]}"


def remove_usernames_from_text(text: str) -> str:
    """
    Removes Reddit username mentions (u/username) from text content.
    
    Args:
        text: The text to clean
    
    Returns:
        Text with username mentions replaced with [USER]
    """
    if pd.isna(text):
        return text
    
    # Remove u/username mentions
    text = re.sub(r'\bu/[A-Za-z0-9_-]+\b', '[USER]', text)
    
    # Remove /r/subreddit mentions if desired (optional - usually kept for context)
    # text = re.sub(r'\br/[A-Za-z0-9_-]+\b', '[SUBREDDIT]', text)
    
    return text


def remove_emails_from_text(text: str) -> str:
    """
    Removes email addresses from text content.
    
    Args:
        text: The text to clean
    
    Returns:
        Text with emails replaced with [EMAIL]
    """
    if pd.isna(text):
        return text
    
    # Basic email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.sub(email_pattern, '[EMAIL]', text)


def remove_phone_numbers_from_text(text: str) -> str:
    """
    Removes phone numbers from text content.
    
    Args:
        text: The text to clean
    
    Returns:
        Text with phone numbers replaced with [PHONE]
    """
    if pd.isna(text):
        return text
    
    # Common phone number patterns
    phone_patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',  # (123) 456-7890
        r'\b\d{10}\b',  # 1234567890
    ]
    
    for pattern in phone_patterns:
        text = re.sub(pattern, '[PHONE]', text)
    
    return text


def anonymize_dataframe(df: pd.DataFrame, 
                       author_column: str = 'author',
                       text_columns: list = None,
                       hash_authors: bool = True,
                       remove_pii: bool = True) -> pd.DataFrame:
    """
    Anonymizes a Reddit DataFrame by hashing usernames and removing PII from text.
    
    Preconditions:
    - df must be a Pandas DataFrame
    - author_column must exist if hash_authors is True
    - text_columns must exist in df if specified
    
    Postconditions:
    - Returns an anonymized DataFrame
    
    Args:
        df: The DataFrame to anonymize
        author_column: Column containing usernames (default: 'author')
        text_columns: List of text columns to clean (e.g., ['body', 'selftext', 'title'])
        hash_authors: Whether to hash author usernames
        remove_pii: Whether to remove PII from text content
    
    Returns:
        Anonymized DataFrame
    """
    df = df.copy()
    
    # Hash author usernames
    if hash_authors and author_column in df.columns:
        print(f"Hashing {author_column} column...")
        df[author_column] = df[author_column].apply(hash_username)
    
    # Remove PII from text columns
    if remove_pii and text_columns:
        for col in text_columns:
            if col in df.columns:
                print(f"Removing PII from {col} column...")
                df[col] = df[col].apply(remove_usernames_from_text)
                df[col] = df[col].apply(remove_emails_from_text)
                df[col] = df[col].apply(remove_phone_numbers_from_text)
    
    # Remove potentially identifying metadata columns (optional)
    # Uncomment if you want to remove these:
    # identifying_columns = ['author_fullname', 'author_flair_text', 'author_premium']
    # for col in identifying_columns:
    #     if col in df.columns:
    #         df = df.drop(columns=[col])
    
    return df


def anonymize_reddit_data(comments_df: pd.DataFrame = None,
                          submissions_df: pd.DataFrame = None) -> tuple:
    """
    Anonymizes both comments and submissions DataFrames.
    
    Args:
        comments_df: Comments DataFrame (optional)
        submissions_df: Submissions DataFrame (optional)
    
    Returns:
        Tuple of (anonymized_comments_df, anonymized_submissions_df)
    """
    anonymized_comments = None
    anonymized_submissions = None
    
    if comments_df is not None and not comments_df.empty:
        print("Anonymizing comments...")
        anonymized_comments = anonymize_dataframe(
            comments_df,
            author_column='author',
            text_columns=['body'],
            hash_authors=True,
            remove_pii=True
        )
        print(f"Comments anonymized: {len(anonymized_comments)} rows")
    
    if submissions_df is not None and not submissions_df.empty:
        print("Anonymizing submissions...")
        anonymized_submissions = anonymize_dataframe(
            submissions_df,
            author_column='author',
            text_columns=['selftext', 'title'],
            hash_authors=True,
            remove_pii=True
        )
        print(f"Submissions anonymized: {len(anonymized_submissions)} rows")
    
    return anonymized_comments, anonymized_submissions


if __name__ == "__main__":
    # Example usage
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Anonymize Reddit data CSVs")
    parser.add_argument("--comments_file", type=str, help="Path to comments CSV file")
    parser.add_argument("--submissions_file", type=str, help="Path to submissions CSV file")
    parser.add_argument("--output_dir", type=str, default="./anonymized_data", 
                       help="Directory to save anonymized data")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    comments_df = None
    submissions_df = None
    
    if args.comments_file:
        print(f"Loading comments from {args.comments_file}...")
        comments_df = pd.read_csv(args.comments_file)
    
    if args.submissions_file:
        print(f"Loading submissions from {args.submissions_file}...")
        submissions_df = pd.read_csv(args.submissions_file)
    
    anonymized_comments, anonymized_submissions = anonymize_reddit_data(
        comments_df, submissions_df
    )
    
    if anonymized_comments is not None:
        output_path = os.path.join(args.output_dir, "anonymized_comments.csv")
        anonymized_comments.to_csv(output_path, index=False)
        print(f"Anonymized comments saved to {output_path}")
    
    if anonymized_submissions is not None:
        output_path = os.path.join(args.output_dir, "anonymized_submissions.csv")
        anonymized_submissions.to_csv(output_path, index=False)
        print(f"Anonymized submissions saved to {output_path}")
