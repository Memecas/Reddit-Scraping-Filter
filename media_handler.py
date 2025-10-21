
import pandas as pd

def clean_media_posts(submissions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans image and video posts in the submissions DataFrame by removing media content
    while retaining both the title and text portion of the post.

    Preconditions:
    - `submissions_df` must be a Pandas DataFrame containing submission data.
    - Expected columns include `is_video`, `url`, `title`, `selftext`, `media`, `media_embed`.

    Postconditions:
    - Returns a DataFrame where media-related fields for image/video posts are cleared.
    - Both the `title` and `selftext` content of these posts are preserved.

    Invariants:
    - Non-media posts are not altered.
    - Post titles are always preserved regardless of media content.
    """
    df = submissions_df.copy()

    # Identify image/video posts. Assuming 'is_video' or 'url' pointing to media indicates a media post.
    # Also consider 'is_self' to differentiate self-posts with text from pure media posts.
    # For now, we'll focus on 'is_video' and common image/video URL patterns.
    # The user specified to remove the image/video but maintain the text. This implies that if 'selftext' exists,
    # it should be kept, and media-specific fields should be cleared.

    # Check for 'is_video' column
    if 'is_video' in df.columns:
        media_posts_mask = df['is_video'] == True
    else:
        media_posts_mask = pd.Series([False] * len(df), index=df.index)

    # Check for common image/video extensions in 'url' column for non-self posts
    if 'url' in df.columns:
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        video_extensions = ('.mp4', '.webm', '.gifv', '.mov')
        # Exclude self-posts from URL-based media detection if 'is_self' exists
        if 'is_self' in df.columns:
            url_media_mask = df['url'].astype(str).str.lower().str.endswith(image_extensions + video_extensions) & (df['is_self'] == False)
        else:
            url_media_mask = df['url'].astype(str).str.lower().str.endswith(image_extensions + video_extensions)
        media_posts_mask = media_posts_mask | url_media_mask

    # Apply cleaning to identified media posts
    if 'url' in df.columns:
        df.loc[media_posts_mask, 'url'] = None # Clear the URL if it was a direct media link
    if 'is_video' in df.columns:
        df.loc[media_posts_mask, 'is_video'] = False # Mark as not a video
    if 'media' in df.columns:
        df.loc[media_posts_mask, 'media'] = None # Clear media object
    if 'media_embed' in df.columns:
        df.loc[media_posts_mask, 'media_embed'] = df.loc[media_posts_mask, 'media_embed'].astype(str).apply(lambda x: '{}') # Clear media embed object
    if 'thumbnail' in df.columns:
        df.loc[media_posts_mask, 'thumbnail'] = df.loc[media_posts_mask, 'thumbnail'].astype(str).apply(lambda x: 'self') # Set thumbnail to 'self' or a generic placeholder

    # Ensure both title and selftext are maintained
    # We explicitly preserve these fields, though they weren't being modified anyway
    if 'title' in df.columns and 'selftext' in df.columns:
        # We don't modify these fields for media posts, but we ensure they're preserved
        # by explicitly selecting them in our DataFrame operations
        preserved_fields = ['title', 'selftext']
        for field in preserved_fields:
            if field in df.columns:
                df[field] = df[field]  # This line explicitly preserves the field

    return df


