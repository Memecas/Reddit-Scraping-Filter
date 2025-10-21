import pandas as pd
import argparse
import os

from data_loader import load_comments_from_csv, load_submissions_from_csv
from media_handler import clean_media_posts
from core_filters import (
    filter_by_score,
    filter_url_only_content,
    filter_edited_content,
    eliminate_duplicates,
    filter_automoderator_and_bots,
    replace_urls_with_token
)
from language_filter import (
    filter_non_english,
    filter_idioms,
    filter_min_word_count
)
from anonymization import anonymize_reddit_data

def main():
    parser = argparse.ArgumentParser(description="Clean and filter Reddit subreddit dumps.")
    parser.add_argument("--comments_file", type=str, required=True, help="Path to the comments CSV file.")
    parser.add_argument("--submissions_file", type=str, required=True, help="Path to the submissions CSV file.")
    parser.add_argument("--output_dir", type=str, default="./filtered_data", help="Directory to save filtered data.")
    parser.add_argument("--min_score", type=int, default=2, help="Minimum score for posts/comments.")
    parser.add_argument("--min_comment_words", type=int, default=10, help="Minimum word count for comments.")
    parser.add_argument("--idioms_to_filter", type=str, nargs="+", default=[],
                        help="List of idioms to filter out (e.g., 'lol' 'rofl').")
    parser.add_argument("--filter_edited", action="store_true",
                        help="Only keep edited comments (filters out non-edited content).")
    parser.add_argument("--filter_language", action="store_true",
                        help="Enable language filtering.")
    parser.add_argument("--target_language", type=str, default="en",
                        help="Target language code (e.g., 'en' for English, 'es' for Spanish). Default is 'en'.")
    parser.add_argument("--anonymize", action="store_true", 
                        help="Anonymize data by hashing usernames and removing PII.")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("Loading data...")
    comments_df = load_comments_from_csv(args.comments_file)
    submissions_df = load_submissions_from_csv(args.submissions_file)

    if comments_df.empty and submissions_df.empty:
        print("No data loaded. Exiting.")
        return

    print("Initial comments count:", len(comments_df))
    print("Initial submissions count:", len(submissions_df))

    print("\nApplying filters to submissions...")
    # 1. Clean image and video posts (maintain text)
    submissions_df = clean_media_posts(submissions_df)
    print("Submissions after media cleaning:", len(submissions_df))

    # 2. Remove removed or deleted posts
    if 'removed_by_category' in submissions_df.columns:
        submissions_df = submissions_df[submissions_df['removed_by_category'].isna()].copy()
    if 'selftext' in submissions_df.columns:
        submissions_df = submissions_df[~submissions_df['selftext'].isin(['[removed]', '[deleted]'])].copy()

    # 3. At least score of 2
    submissions_df = filter_by_score(submissions_df, args.min_score)

    # 4. Remove posts containing only url links
    submissions_df = filter_url_only_content(submissions_df, text_column='selftext')
    
    # 4a. Replace remaining URLs with tokens in both selftext and title
    if 'selftext' in submissions_df.columns:
        submissions_df['selftext'] = submissions_df['selftext'].fillna('').apply(replace_urls_with_token)
    if 'title' in submissions_df.columns:
        submissions_df['title'] = submissions_df['title'].fillna('').apply(replace_urls_with_token)

    # 5. Eliminate duplicates
    submissions_df = eliminate_duplicates(submissions_df, subset_cols=['id'])

    # 6. Eliminate comments from automoderators and bots
    submissions_df = filter_automoderator_and_bots(submissions_df, author_column='author')

    # 7. Min word count for selftext (using the same minimum as comments)
    submissions_df = filter_min_word_count(submissions_df, min_n_words=args.min_comment_words, text_column='selftext')

    # 8. Language filtering (if enabled)
    if args.filter_language:
        print(f"Filtering submissions for {args.target_language} language content...")
        submissions_df = filter_non_english(submissions_df, text_column='selftext', target_lang=args.target_language)
        submissions_df = filter_non_english(submissions_df, text_column='title', target_lang=args.target_language)

    print(f"Final submissions count after filtering: {len(submissions_df)}")

    print("\nApplying filters to comments...")
    # 1. Remove removed or deleted comments
    if 'body' in comments_df.columns:
        comments_df = comments_df[~comments_df['body'].isin(['[removed]', '[deleted]'])].copy()

    # 2. At least score of 2
    comments_df = filter_by_score(comments_df, args.min_score)

    # 3. Remove comments containing only url links
    comments_df = filter_url_only_content(comments_df, text_column='body')
    
    # 3a. Replace remaining URLs with tokens in comment body
    if 'body' in comments_df.columns:
        comments_df['body'] = comments_df['body'].fillna('').apply(replace_urls_with_token)

    # 4. Edited comments to show content that the users had full attention on writing it
    if args.filter_edited:
        comments_df = filter_edited_content(comments_df)

    # 5. Eliminate duplicates
    comments_df = eliminate_duplicates(comments_df, subset_cols=['id'])

    # 6. Eliminate comments from automoderators and bots
    comments_df = filter_automoderator_and_bots(comments_df, author_column='author')

    # 7. Eliminate other idioms
    comments_df = filter_idioms(comments_df, text_column='body', idioms_list=args.idioms_to_filter)

    # 8. Min word count for comments
    comments_df = filter_min_word_count(comments_df, args.min_comment_words)

    # 9. Language filtering (if enabled)
    if args.filter_language:
        print(f"Filtering comments for {args.target_language} language content...")
        comments_df = filter_non_english(comments_df, text_column='body', target_lang=args.target_language)

    print(f"Final comments count after filtering: {len(comments_df)}")

    # Anonymization step (if requested)
    if args.anonymize:
        print("\n" + "="*50)
        print("Anonymizing data...")
        print("="*50)
        comments_df, submissions_df = anonymize_reddit_data(comments_df, submissions_df)

    print("\nSaving filtered data...")
    
    # Extract original filenames without path
    comments_filename = os.path.basename(args.comments_file)
    submissions_filename = os.path.basename(args.submissions_file)
    
    # Remove extension and add 'filtered_' prefix
    comments_name = os.path.splitext(comments_filename)[0]
    submissions_name = os.path.splitext(submissions_filename)[0]
    
    comments_output_path = os.path.join(args.output_dir, f"filtered_{comments_name}.csv")
    submissions_output_path = os.path.join(args.output_dir, f"filtered_{submissions_name}.csv")
    
    comments_df.to_csv(comments_output_path, index=False)
    submissions_df.to_csv(submissions_output_path, index=False)

    print(f"\n✓ Filtered comments saved to {comments_output_path}")
    print(f"✓ Filtered submissions saved to {submissions_output_path}")
    
    if args.anonymize:
        print("\n✓ Data has been anonymized (usernames hashed, PII removed)")

if __name__ == "__main__":
    main()