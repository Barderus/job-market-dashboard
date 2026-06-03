import ast
import os
import re

import matplotlib
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter


matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_JOBS_PATH = "Data/merger/data_jobs.csv"
JOB_MARKET_PATH = "Data/processed/job_market_processed_data.csv"
OUTPUT_DIR = "Visualization"
MARKET_SCOPE = "2023 U.S.-Only Job Market"
TITLE_COLOR = "#102542"
FIGURE_BG = "#f7f3ea"
AXIS_BG = "#fffdf8"
ACCENT_BLUE = "#1b4965"
ACCENT_TEAL = "#3a7d44"
ACCENT_CORAL = "#d96c4f"
ACCENT_GOLD = "#c2872c"
ACCENT_RED = "#b23a48"
ACCENT_PLUM = "#6c4f77"

SOFT_SKILL_PHRASES = {
    "communication": ["communication", "communicate effectively", "verbal and written"],
    "leadership": ["leadership", "lead teams", "manage teams", "team lead"],
    "teamwork": ["teamwork", "collaboration", "cross-functional"],
    "problem solving": ["problem solving", "analytical skills", "solve problems"],
    "time management": ["time management", "prioritize tasks"],
    "adaptability": ["adaptability", "adapt to change", "flexible"],
    "critical thinking": ["critical thinking", "strategic thinking"],
    "interpersonal skills": ["interpersonal skills", "people skills", "relationship building"],
    "customer focus": ["customer service", "client interaction", "customer support", "customer-centric"],
    "attention to detail": ["attention to detail", "detail-oriented", "detail oriented"],
}


def parse_skill_list(value: object) -> list[str]:
    if pd.isna(value):
        return []

    text = str(value).strip()
    if not text or text == "[]":
        return []

    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        parsed = [part.strip() for part in text.split(",") if part.strip()]

    if not isinstance(parsed, list):
        return []

    cleaned = []
    for item in parsed:
        skill = str(item).strip().lower()
        if skill:
            cleaned.append(skill)
    return cleaned


def project_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


def prepare_data_jobs(path: str) -> pd.DataFrame:
    df = pd.read_csv(project_path(path))
    df["data_source"] = "data_jobs"
    df["job_company"] = df["company_name"]
    df["description_clean"] = ""
    df["state"] = ""
    df["salary_value"] = pd.to_numeric(df["salary_year_avg"], errors="coerce")

    hourly_salary = pd.to_numeric(df.get("salary_hour_avg"), errors="coerce") * 2080
    df["salary_value"] = df["salary_value"].fillna(hourly_salary)

    if "job_title_short" in df.columns:
        df["role_name"] = df["job_title_short"].fillna(df["job_title"])
    else:
        df["role_name"] = df["job_title"]

    df["parsed_skills"] = df["job_skills"].apply(parse_skill_list)
    return df


def prepare_job_market(path: str) -> pd.DataFrame:
    df = pd.read_csv(project_path(path))
    df["data_source"] = "job_market"
    df["salary_value"] = pd.to_numeric(df["salary_avg"], errors="coerce")
    df["job_company"] = df["job_company"].fillna("Unknown").astype(str).str.strip()
    df["description_clean"] = df.get("description_clean", "").fillna("").astype(str).str.lower()
    df["state"] = df.get("state", "").fillna("").astype(str).str.strip()
    df["role_name"] = df["job_title"]

    skill_source = "job_skills" if "job_skills" in df.columns else "skills"
    df["parsed_skills"] = df[skill_source].apply(parse_skill_list)
    return df


def load_merged_dataset() -> pd.DataFrame:
    data_jobs_df = prepare_data_jobs(DATA_JOBS_PATH)
    job_market_df = prepare_job_market(JOB_MARKET_PATH)

    merged_df = pd.concat([data_jobs_df, job_market_df], ignore_index=True, sort=False)
    merged_df["job_company"] = merged_df["job_company"].fillna("Unknown").astype(str).str.strip()
    merged_df["job_title"] = merged_df["job_title"].fillna("Unknown").astype(str).str.strip()
    merged_df["role_name"] = merged_df["role_name"].fillna(merged_df["job_title"]).astype(str).str.strip()
    merged_df["job_country"] = merged_df.get("job_country", "").fillna("").astype(str).str.strip()
    merged_df["state"] = merged_df["state"].fillna("").astype(str).str.strip()
    return merged_df


def filter_us_only(df: pd.DataFrame) -> pd.DataFrame:
    country_text = df["job_country"].fillna("").astype(str)
    return df[country_text.str.contains("United States", case=False, na=False)].copy()


def top_technical_skills(df: pd.DataFrame, limit: int = 10) -> pd.Series:
    exploded = df["parsed_skills"].explode().dropna()
    return exploded.value_counts().head(limit).sort_values()


def top_soft_skills(df: pd.DataFrame, limit: int = 10) -> pd.Series:
    description_series = df["description_clean"].fillna("")
    counts: dict[str, int] = {}

    for skill, phrases in SOFT_SKILL_PHRASES.items():
        pattern = "|".join(re.escape(phrase) for phrase in phrases)
        counts[skill] = int(description_series.str.contains(pattern, regex=True, na=False).sum())

    return pd.Series(counts).sort_values(ascending=False).head(limit).sort_values()


def roles_in_demand(df: pd.DataFrame, limit: int = 10) -> pd.Series:
    return df["role_name"].value_counts().head(limit).sort_values()


def roles_by_pay(df: pd.DataFrame, limit: int = 10, min_salary_posts: int = 10) -> pd.DataFrame:
    salary_df = df.dropna(subset=["salary_value"]).copy()
    role_stats = (
        salary_df.groupby("role_name")
        .agg(avg_salary=("salary_value", "mean"), salary_posts=("salary_value", "size"))
        .query("salary_posts >= @min_salary_posts")
        .sort_values("avg_salary", ascending=False)
        .head(limit)
        .sort_values("avg_salary")
    )
    return role_stats.reset_index()


def entry_level_roles_by_pay(df: pd.DataFrame, limit: int = 10, min_salary_posts: int = 5) -> pd.DataFrame:
    salary_df = df.dropna(subset=["salary_value"]).copy()
    role_text = salary_df["role_name"].fillna("").astype(str)

    include_pattern = r"junior|entry|intern|associate|new grad|graduate|trainee|early career"
    exclude_pattern = r"senior|sr\.?|staff|principal|lead|manager|director|vp|vice president|head|chief"

    filtered = salary_df[
        role_text.str.contains(include_pattern, case=False, na=False)
        & ~role_text.str.contains(exclude_pattern, case=False, na=False)
    ].copy()

    role_stats = (
        filtered.groupby("role_name")
        .agg(avg_salary=("salary_value", "mean"), salary_posts=("salary_value", "size"))
        .query("salary_posts >= @min_salary_posts")
        .sort_values("avg_salary", ascending=False)
        .head(limit)
        .sort_values("avg_salary")
    )
    return role_stats.reset_index()


def top_paying_companies(df: pd.DataFrame, limit: int = 10, min_salary_posts: int = 3) -> pd.DataFrame:
    salary_df = df.dropna(subset=["salary_value"]).copy()
    company_stats = (
        salary_df.groupby("job_company")
        .agg(avg_salary=("salary_value", "mean"), salary_posts=("salary_value", "size"))
        .query("salary_posts >= @min_salary_posts")
        .sort_values("avg_salary", ascending=False)
        .head(limit)
        .sort_values("avg_salary")
    )
    return company_stats.reset_index()


def apply_chart_style(fig: plt.Figure, ax: plt.Axes) -> None:
    fig.patch.set_facecolor(FIGURE_BG)
    ax.set_facecolor(AXIS_BG)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d9cbb6")
    ax.spines["bottom"].set_color("#d9cbb6")
    ax.grid(axis="x", linestyle="--", alpha=0.18, color="#7f6a58")
    ax.tick_params(colors=TITLE_COLOR, labelsize=11)
    ax.xaxis.label.set_color(TITLE_COLOR)
    ax.yaxis.label.set_color(TITLE_COLOR)


def format_dollars(x: float, _pos: int) -> str:
    return f"${x:,.0f}"


def create_salary_distribution(df: pd.DataFrame) -> plt.Figure:
    salary_df = df.dropna(subset=["salary_value"]).copy()
    upper_bound = salary_df["salary_value"].quantile(0.99)
    clipped = salary_df[salary_df["salary_value"] <= upper_bound]["salary_value"]
    median_salary = clipped.median()

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.histplot(clipped, bins=35, kde=True, color=ACCENT_BLUE, edgecolor=AXIS_BG, linewidth=1.0, ax=ax)
    ax.axvline(median_salary, color=ACCENT_RED, linestyle="--", linewidth=2.5)
    ax.text(
        median_salary,
        ax.get_ylim()[1] * 0.92,
        f"Median ${median_salary:,.0f}",
        color=ACCENT_RED,
        fontsize=11,
        fontweight="bold",
        ha="left",
    )
    ax.set_title(f"Salary Distribution\n{MARKET_SCOPE}", fontsize=18, fontweight="bold", color=TITLE_COLOR, pad=16)
    ax.set_xlabel("Annual Salary in U.S. Dollars")
    ax.set_ylabel("Number of Job Postings")
    ax.xaxis.set_major_formatter(FuncFormatter(format_dollars))
    apply_chart_style(fig, ax)
    return fig


def create_series_bar_chart(series: pd.Series, title: str, xlabel: str, color: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(x=series.values, y=series.index, color=color, saturation=0.95, ax=ax)
    ax.set_title(f"{title}\n{MARKET_SCOPE}", fontsize=18, fontweight="bold", color=TITLE_COLOR, pad=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", padding=6, color=TITLE_COLOR, fontsize=10)
    apply_chart_style(fig, ax)
    return fig


def create_dataframe_bar_chart(df: pd.DataFrame, y_column: str, x_column: str, title: str, xlabel: str, color: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 7))
    labels = df[y_column].astype(str).str.slice(0, 45)
    sns.barplot(x=df[x_column], y=labels, color=color, saturation=0.95, ax=ax)
    ax.set_title(f"{title}\n{MARKET_SCOPE}", fontsize=18, fontweight="bold", color=TITLE_COLOR, pad=16)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(format_dollars))
    for container in ax.containers:
        ax.bar_label(container, fmt="$%.0f", padding=6, color=TITLE_COLOR, fontsize=10)
    apply_chart_style(fig, ax)
    return fig


def create_facts_panel(df: pd.DataFrame, skills: pd.Series, roles_pay_df: pd.DataFrame) -> plt.Figure:
    salary_df = df.dropna(subset=["salary_value"]).copy()
    salary_coverage = df["salary_value"].notna().mean() * 100
    most_common_role = df["role_name"].value_counts().idxmax()
    most_common_role_count = int(df["role_name"].value_counts().iloc[0])
    most_requested_skill = skills.index[-1] if not skills.empty else "N/A"
    most_requested_skill_count = int(skills.iloc[-1]) if not skills.empty else 0
    median_salary = salary_df["salary_value"].median() if not salary_df.empty else 0
    top_paid_role = roles_pay_df.iloc[-1]["role_name"] if not roles_pay_df.empty else "N/A"
    top_paid_role_salary = roles_pay_df.iloc[-1]["avg_salary"] if not roles_pay_df.empty else 0

    facts = [
        f"Most common role: {most_common_role} ({most_common_role_count:,} postings)",
        f"Most requested technical skill: {most_requested_skill.title()} ({most_requested_skill_count:,} postings)",
        f"Median advertised salary: ${median_salary:,.0f}",
        f"Highest-paying role in the filtered chart: {top_paid_role} (${top_paid_role_salary:,.0f} avg.)",
        f"Salary data coverage: {salary_coverage:.1f}% of postings",
    ]

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis("off")
    fig.patch.set_facecolor(FIGURE_BG)
    ax.set_facecolor(AXIS_BG)
    ax.set_title(
        f"Interesting Facts For Students\n{MARKET_SCOPE}",
        loc="left",
        fontsize=18,
        fontweight="bold",
        color=TITLE_COLOR,
        pad=16,
    )
    ax.text(
        0.03,
        0.92,
        "\n\n".join(facts),
        va="top",
        ha="left",
        fontsize=13,
        color=TITLE_COLOR,
        wrap=True,
        bbox={"boxstyle": "round,pad=0.7", "facecolor": "#fff8ef", "edgecolor": "#d9cbb6"},
    )
    return fig


def save_figure(fig: plt.Figure, filename: str) -> str:
    output_dir = project_path(OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    sns.set_theme(style="whitegrid", rc={"axes.edgecolor": "#d9cbb6", "grid.color": "#d9cbb6"})
    df = filter_us_only(load_merged_dataset())

    technical_skills = top_technical_skills(df)
    soft_skills = top_soft_skills(df)
    demand_roles = roles_in_demand(df)
    paid_roles = entry_level_roles_by_pay(df)
    paying_companies = top_paying_companies(df)

    output_files = [
        save_figure(create_salary_distribution(df), "salary_distribution.png"),
        save_figure(
            create_series_bar_chart(
                technical_skills,
                "Top 10 Technical Skills (Merged job_skills Lists)",
                "Job Postings",
                "#2a9d8f",
            ),
            "top_10_technical_skills.png",
        ),
        save_figure(
            create_series_bar_chart(
                soft_skills,
                "Top 10 Soft Skills (Description Text Only)",
                "Mentions in Descriptions",
                "#e76f51",
            ),
            "top_10_soft_skills.png",
        ),
        save_figure(
            create_series_bar_chart(demand_roles, "Roles In Demand", "Job Postings", "#457b9d"),
            "roles_in_demand.png",
        ),
        save_figure(
            create_dataframe_bar_chart(
                paid_roles,
                "role_name",
                "avg_salary",
                "Entry-Level Roles By Pay",
                "Average Salary (USD)",
                ACCENT_PLUM,
            ),
            "roles_by_pay.png",
        ),
        save_figure(
            create_dataframe_bar_chart(
                paying_companies,
                "job_company",
                "avg_salary",
                "Top 10 Paying Companies",
                "Average Salary (USD)",
                ACCENT_GOLD,
            ),
            "top_10_paying_companies.png",
        ),
        save_figure(create_facts_panel(df, technical_skills, paid_roles), "interesting_facts_for_students.png"),
    ]

    print("Saved files:")
    for file_path in output_files:
        print(file_path)
    print(f"US-only rows used: {len(df):,}")


if __name__ == "__main__":
    main()
