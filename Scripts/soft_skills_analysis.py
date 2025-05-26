import pandas as pd
import re

SOFT_SKILL_PHRASES = {
    'communication': ['communication', 'communicate effectively', 'verbal and written'],
    'leadership': ['leadership', 'lead teams', 'manage teams', 'team lead'],
    'teamwork': ['teamwork', 'collaboration', 'work with cross-functional teams'],
    'problem-solving': ['problem solving', 'analytical skills', 'solve problems'],
    'time management': ['time management', 'prioritize tasks'],
    'adaptability': ['adaptability', 'adapt to change', 'flexible'],
    'critical thinking': ['critical thinking', 'strategic thinking'],
    'interpersonal skills': ['interpersonal skills', 'people skills', 'relationship building'],
    'customer focus': ['customer service', 'client interaction', 'customer support', 'customer-centric']
}

def count_soft_skills(df, column='Description_clean'):
    """
    Count soft skill mentions across job descriptions.

    Returns:
        DataFrame with skill and frequency.
    """
    counts = {}

    # For each soft skill, build a regex pattern from its associated phrases and count matches
    for skill, phrases in SOFT_SKILL_PHRASES.items():
        pattern = '|'.join([re.escape(p) for p in phrases])
        counts[skill] = df[column].str.contains(pattern, regex=True).sum()

    # Convert the counts dictionary to a sorted DataFrame
    return pd.DataFrame(counts.items(), columns=['Soft Skill / Responsibility', 'Mentions']).sort_values(by='Mentions', ascending=False)

