import pandas as pd
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('stopwords')

def extract_action_verbs(df, text_column='Description_clean', top_n=20):
    """
    Extract common action verbs from job descriptions.

    Returns:
        DataFrame with verbs and frequencies.
    """
    # Combine and clean all text
    text = ' '.join(df[text_column].dropna()).lower()
    text = re.sub(r'[^a-z\s]', '', text)  # Corrected regex

    # Tokenize and tag
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)

    # Remove stopwords and keep verb tags
    stop_words = set(stopwords.words('english'))
    verb_tags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}  # all verb forms
    action_verbs = [word for word, tag in tagged if tag in verb_tags and word not in stop_words]

    # Count and return
    counter = Counter(action_verbs)
    return pd.DataFrame(counter.most_common(top_n), columns=['Verb', 'Mentions'])
