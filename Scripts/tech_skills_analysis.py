import pandas as pd
import re

SKILL_VARIATIONS = {
    'python': {'python', 'python3', 'python 3', 'python programming'},
    'java': {'java', 'java programming'},
    'javascript': {'javascript', 'js'},
    'typescript': {'typescript', 'ts'},
    'c++': {'c++', 'cpp', 'c plus plus'},
    'c#': {'c#', 'c sharp'},
    'go': {'go', 'golang'},
    'r': {'r', 'r programming'},
    'react': {'react', 'reactjs'},
    'angular': {'angular', 'angularjs'},
    'django': {'django', 'django framework'},
    'flask': {'flask', 'flask framework'},
    'aws': {'aws', 'amazon web services'},
    'azure': {'azure', 'microsoft azure'},
    'gcp': {'gcp', 'google cloud'},
    'docker': {'docker'},
    'kubernetes': {'kubernetes', 'k8s'},
    'sql': {'sql'},
    'postgresql': {'postgresql', 'postgres'},
    'mysql': {'mysql'},
    'mongodb': {'mongodb'},
    'redis': {'redis'},
    'git': {'git'},
    'linux': {'linux'},
    'excel': {'excel', 'microsoft excel'},
    'api': {'api', 'rest api'},
    'tableau': {'tableau'},
    'power bi': {'power bi', 'powerbi'}
}

CATEGORY_MAP = {
    'python': 'Programming Language',
    'java': 'Programming Language',
    'javascript': 'Programming Language',
    'typescript': 'Programming Language',
    'c++': 'Programming Language',
    'c#': 'Programming Language',
    'go': 'Programming Language',
    'r': 'Programming Language',

    'react': 'Framework',
    'angular': 'Framework',
    'django': 'Framework',
    'flask': 'Framework',

    'aws': 'Cloud',
    'azure': 'Cloud',
    'gcp': 'Cloud',

    'docker': 'DevOps',
    'kubernetes': 'DevOps',
    'git': 'DevOps',

    'sql': 'Database',
    'postgresql': 'Database',
    'mysql': 'Database',
    'mongodb': 'Database',
    'redis': 'Database',

    'tableau': 'BI Tool',
    'power bi': 'BI Tool',
    'excel': 'BI Tool',

    'api': 'Other',
    'linux': 'Other'
}

def extract_tech_skills(df, text_column='Description'):
    """
    Extract and count mentions of tech skills in job descriptions.
    Returns a DataFrame of skills and their frequencies.
    """
    keyword_counts = {}

    # For each skill, build a regex pattern from its known variations and count how many descriptions mention it
    for skill, variations in SKILL_VARIATIONS.items():
        pattern = '|'.join([re.escape(v) for v in variations])
        mask = df[text_column].str.contains(pattern, case=False, regex=True, na=False)
        keyword_counts[skill] = mask.sum()

    # Convert the results to a DataFrame and sort by number of mentions
    df_skills = pd.DataFrame(keyword_counts.items(), columns=['Skill', 'Mentions'])
    df_skills = df_skills.sort_values(by='Mentions', ascending=False).reset_index(drop=True)
    return df_skills


def categorize_skills(df_skills):
    """
    Map each skill to a category and return a grouped summary.
    """
    df_skills['Category'] = df_skills['Skill'].map(CATEGORY_MAP).fillna('Other')
    return df_skills.sort_values(['Category', 'Mentions'], ascending=[True, False])