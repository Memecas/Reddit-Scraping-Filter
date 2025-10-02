
import pandas as pd
import re

def filter_parenting_content(df: pd.DataFrame, text_column: str = 'body') -> pd.DataFrame:
    """
    Filters a DataFrame to retain entries that are likely related to parenting.
    This function looks for keywords in the specified text column.

    Preconditions:
    - `df` must be a Pandas DataFrame containing the `text_column`.

    Postconditions:
    - Returns a DataFrame containing only entries identified as parenting-related.

    Invariants:
    - The original DataFrame is not modified.
    """
    if text_column not in df.columns:
        print(f"Warning: '{text_column}' column not found. Skipping parenting content filtering.")
        return df

    parenting_keywords = [
        'parenting', 'parent', 'child', 'children', 'kid', 'kids', 'baby', 'babies',
        'toddler', 'toddlers', 'teen', 'teens', 'mother', 'father', 'mom', 'dad',
        'family', 'guardian', 'upbringing', 'raising', 'education', 'school',
        'daycare', 'nursery', 'diaper', 'feeding', 'sleep training', 'discipline',
        'emotional support', 'development', 'milestone', 'playdate', 'sibling',
        'newborn', 'infant', 'adolescent', 'co-parenting', 'step-parent', 'foster parent',
        'grandparent', 'caregiver', 'childcare', 'homeschooling', 'potty training',
        'bedtime', 'allowance', 'chores', 'playtime', 'story time', 'pacifier',
        'stroller', 'car seat', 'crib', 'high chair', 'baby food', 'formula',
        'breastfeeding', 'weaning', 'tantrum', 'puberty', 'adolescence', 'teenager',
        'empty nest', 'college fund', 'allowance', 'curfew', 'responsibility',
        'guidance', 'support', 'understanding', 'love', 'patience', 'empathy',
        'communication', 'boundaries', 'routine', 'schedule', 'nurturing', 'bonding',
        'attachment', 'positive reinforcement', 'consequences', 'role model',
        'developmental stages', 'learning', 'growth', 'well-being', 'health',
        'safety', 'nutrition', 'immunization', 'pediatrician', 'doctor', 'therapy',
        'counseling', 'mental health', 'physical health', 'emotional health',
        'behavior', 'temperament', 'personality', 'identity', 'self-esteem',
        'confidence', 'resilience', 'coping skills', 'problem-solving', 'decision-making',
        'independence', 'autonomy', 'social skills', 'friendship', 'bullying',
        'peer pressure', 'online safety', 'screen time', 'digital citizenship',
        'values', 'morals', 'ethics', 'faith', 'culture', 'traditions', 'heritage',
        'celebrations', 'rituals', 'family time', 'quality time', 'vacation', 'travel',
        'adventure', 'exploration', 'discovery', 'creativity', 'imagination',
        'art', 'music', 'sports', 'hobbies', 'interests', 'passion', 'purpose',
        'future', 'dreams', 'goals', 'aspirations', 'success', 'happiness', 'joy',
        'fulfillment', 'meaning', 'legacy', 'generation', 'ancestors', 'descendants',
        'lineage', 'roots', 'history', 'future', 'hope', 'love', 'connection',
        'belonging', 'community', 'support system', 'village', 'tribe', 'network',
        'resources', 'guidance', 'mentorship', 'inspiration', 'motivation',
        'encouragement', 'praise', 'recognition', 'appreciation', 'gratitude',
        'thankfulness', 'kindness', 'compassion', 'generosity', 'sharing',
        'cooperation', 'teamwork', 'collaboration', 'respect', 'tolerance',
        'acceptance', 'inclusion', 'diversity', 'equality', 'justice', 'fairness',
        'peace', 'harmony', 'balance', 'well-being', 'wholeness', 'completeness',
        'unity', 'togetherness', 'oneness', 'interconnectedness', 'universal love'
    ]

    # Create a regex pattern to match any of the keywords, case-insensitive, whole word match
    # Using \b for whole word matching to avoid partial matches (e.g., 'car' in 'careful')
    pattern = re.compile(r'\b(?:' + '|'.join(re.escape(kw) for kw in parenting_keywords) + r')\b', re.IGNORECASE)

    # Filter rows where the text_column contains any of the parenting keywords
    mask = df[text_column].fillna("").apply(lambda x: bool(pattern.search(x)))
    return df[mask].copy()


