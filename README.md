# Reddit Data Filter Pipeline

A modular Python script for cleaning and filtering Reddit subreddit data dumps from Pushshift to extract high-quality content.

## Features

- **Score filtering** - Remove low-quality posts/comments below a minimum score threshold
- **Content quality filters** - Remove URL-only content, bot/automoderator posts, and deleted/removed content
- **Language detection** - Keep only English content using language detection
- **Duplicate removal** - Eliminate duplicate entries
- **Word count filtering** - Enforce minimum word count for comments
- **Optional edited content filtering** - Optionally keep only edited comments (indicating thoughtful content)
- **Idiom filtering** - Remove specific idioms/phrases
- **Media handling** - Clean media posts while preserving text content
- **Anonymization** - Optional username hashing and PII removal

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/reddit-filter-pipeline.git
cd reddit-filter-pipeline

# Install dependencies
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- langdetect >= 1.0.9

## Usage

### Basic Usage

```bash
python main.py \
  --comments_file path/to/comments.csv \
  --submissions_file path/to/submissions.csv
```

### Advanced Options

```bash
python main.py \
  --comments_file data/reddit_comments.csv \
  --submissions_file data/reddit_submissions.csv \
  --output_dir ./filtered_output \
  --min_score 5 \
  --min_comment_words 20 \
  --filter_edited \
  --idioms_to_filter "lol" "rofl" "lmao" \
  --anonymize
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--comments_file` | string | Required | Path to comments CSV file |
| `--submissions_file` | string | Required | Path to submissions CSV file |
| `--output_dir` | string | `./filtered_data` | Output directory for filtered files |
| `--min_score` | int | `2` | Minimum score for posts/comments |
| `--min_comment_words` | int | `10` | Minimum word count for comments |
| `--idioms_to_filter` | list | `[]` | List of idioms/phrases to filter out |
| `--filter_edited` | flag | `False` | Only keep edited comments |
| `--anonymize` | flag | `False` | Anonymize usernames and remove PII |

## Input CSV Columns

### Required Columns - Comments
- `id` - Unique comment identifier
- `body` - Comment text
- `author` - Username
- `score` - Upvote score
- `edited` - Edit status (boolean or timestamp)

### Required Columns - Submissions
- `id` - Unique post identifier
- `title` - Post title
- `selftext` - Post body text
- `author` - Username
- `score` - Upvote score
- `url` - Post URL
- `is_self` - Self-post indicator

### Optional Columns
- `created_utc` - Timestamp
- `subreddit` - Subreddit name
- `removed_by_category` - Removal status
- `media`, `media_embed`, `thumbnail` - Media fields

## Filtering Pipeline

### Submissions Filter Order
1. Clean media posts (preserve text)
2. Remove removed/deleted posts
3. Minimum score filter
4. Remove URL-only posts
5. Eliminate duplicates
6. Remove bots/automoderators
7. English language filter (title + selftext)

### Comments Filter Order
1. Remove removed/deleted comments
2. Minimum score filter
3. Remove URL-only comments
4. Optional: Edited content filter
5. Eliminate duplicates
6. Remove bots/automoderators
7. Idiom filtering
8. Minimum word count
9. English language filter

## Output

The script generates two filtered CSV files:
- `filtered_<original_comments_name>.csv`
- `filtered_<original_submissions_name>.csv`

Files are saved to the specified output directory with the original filename preserved.

## Module Structure

```
.
├── main.py                  # Main script and pipeline orchestration
├── core_filters.py          # Core filtering functions
├── language_filter.py       # Language detection and word count filters
├── media_handler.py         # Media post cleaning
├── data_loader.py           # CSV loading utilities
├── anonymization.py         # Username hashing and PII removal
├── requirements.txt         # Python dependencies
└── README.md
```

## Bot Filtering

Automatically removes posts/comments from common Reddit bots including:
- AutoModerator
- RemindMeBot
- TweetPoster
- And 20+ other known bots

See `core_filters.py` for the complete list.

## Examples

### Filter with higher quality threshold
```bash
python main.py \
  --comments_file comments.csv \
  --submissions_file submissions.csv \
  --min_score 10 \
  --min_comment_words 25
```

### Process with anonymization
```bash
python main.py \
  --comments_file comments.csv \
  --submissions_file submissions.csv \
  --anonymize
```

### Only keep edited comments
```bash
python main.py \
  --comments_file comments.csv \
  --submissions_file submissions.csv \
  --filter_edited
```

### Filter out specific phrases
```bash
python main.py \
  --comments_file comments.csv \
  --submissions_file submissions.csv \
  --idioms_to_filter "tbh" "imo" "imho"
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

Built for processing Reddit data dumps for content quality analysis and research.
