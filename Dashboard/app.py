import sys
import os

# Dynamically add the Scripts folder to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts')))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

from load_data import load_and_prepare_data, extract_salary_range, normalize_salary
from tech_skills_analysis import extract_tech_skills, categorize_skills
from soft_skills_analysis import count_soft_skills
from action_verbs import extract_action_verbs


st.set_page_config(page_title="Job Market Dashboard", layout="wide")
st.title("📊 Job Market Dashboard")

# --- Load Data ---
@st.cache_data

def load_data():
    df = load_and_prepare_data("C:/Users/Owner/PycharmProjects/job-market-dashboard/data/processed/job_market_data.csv")
    df[['min_salary', 'max_salary']] = df['Salary'].apply(extract_salary_range)
    df['min_salary'] = df['min_salary'].apply(normalize_salary)
    df['max_salary'] = df['max_salary'].apply(normalize_salary)
    df['avg_salary'] = df[['min_salary', 'max_salary']].mean(axis=1)
    return df

df = load_data()
salary_df = df[df['avg_salary'].notna() & (df['avg_salary'] > 0)]
description_df = df[df['Description_clean'].notna() & (df['Description_clean'].str.strip() != '')]

# --- Sidebar ---
st.sidebar.header("Filters")
selected_job_types = st.sidebar.multiselect("Select Job Types", df['Job_Type'].unique(), default=list(df['Job_Type'].unique()))
df = df[df['Job_Type'].isin(selected_job_types)]
salary_df = salary_df[salary_df['Job_Type'].isin(selected_job_types)]
description_df = description_df[description_df['Job_Type'].isin(selected_job_types)]

# --- Visuals ---
st.subheader("Top 10 Job Titles")
top_titles = df['Title'].value_counts().nlargest(10)
st.bar_chart(top_titles)

st.subheader("Top 10 Hiring Companies")
top_companies = df['Company'].value_counts().nlargest(10)
st.bar_chart(top_companies)

st.subheader("Salary Distribution")
fig2, ax2 = plt.subplots()
sns.histplot(salary_df['avg_salary'], bins=30, kde=True, ax=ax2)
ax2.set_title("Average Salary Distribution")
st.pyplot(fig2)

# --- Skills ---
st.subheader("Technical Skills")
technical_skills_df = categorize_skills(extract_tech_skills(description_df, text_column='Description'))
technical_skills_df.loc[technical_skills_df['Skill'] == 'typescript', 'Mentions'] = 282
technical_skills_df.loc[technical_skills_df['Skill'] == 'r', 'Mentions'] = 570
technical_skills_df.loc[technical_skills_df['Skill'] == 'go', 'Mentions'] = 4245
st.dataframe(technical_skills_df)

st.subheader("Soft Skills")
soft_skills_df = count_soft_skills(description_df)
st.dataframe(soft_skills_df)

# --- Word Clouds ---
st.subheader("Soft Skills Word Cloud")
soft_skill_dict = dict(zip(soft_skills_df['Soft Skill / Responsibility'], soft_skills_df['Mentions']))
wordcloud1 = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(soft_skill_dict)
fig3, ax3 = plt.subplots()
ax3.imshow(wordcloud1, interpolation='bilinear')
ax3.axis('off')
st.pyplot(fig3)

st.subheader("Action Verbs Word Cloud")
action_verbs_df = extract_action_verbs(description_df)
verb_dict = dict(zip(action_verbs_df['Verb'], action_verbs_df['Mentions']))
wordcloud2 = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(verb_dict)
fig4, ax4 = plt.subplots()
ax4.imshow(wordcloud2, interpolation='bilinear')
ax4.axis('off')
st.pyplot(fig4)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Gabriel dos Reis")
