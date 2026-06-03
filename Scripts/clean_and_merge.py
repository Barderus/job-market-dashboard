import argparse
import glob
import hashlib
import os
import re
from typing import Iterable

import pandas as pd

from load_data import extract_salary_range, normalize_salary
from tech_skills_analysis import extract_skills_from_text


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_INPUT_DIRS = [
    "Data/raw",
    "Workflow",
]
DEFAULT_OUTPUT = "Data/processed/job_market_processed_data.csv"

STANDARD_COLUMNS = [
    "source",
    "search_term",
    "search_location",
    "source_url",
    "scraped_at",
    "title",
    "company_name",
    "job_location",
    "job_type",
    "salary",
    "description",
]

OUTPUT_COLUMNS = [
    "source",
    "search_term",
    "search_location",
    "source_url",
    "scraped_at",
    "job_title",
    "job_location",
    "job_company",
    "job_schedule_type",
    "Salary",
    "description_clean",
    "min_salary",
    "max_salary",
    "salary_avg",
    "has_salary",
    "has_description",
    "city",
    "state",
    "job_country",
    "skills",
    "job_skills",
]

MIN_DESCRIPTION_KEY_CHARS = 40

LEGACY_COLUMN_ALIASES = {
    "title": "title",
    "job_title": "title",
    "Title": "title",
    "company_name": "company_name",
    "Company Name": "company_name",
    "Company": "company_name",
    "job_company": "company_name",
    "job_location": "job_location",
    "Job Location": "job_location",
    "Location": "job_location",
    "job_type": "job_type",
    "Job Type": "job_type",
    "job_schedule_type": "job_type",
    "Salary": "salary",
    "salary": "salary",
    "job_salary": "salary",
    "Description": "description",
    "description": "description",
    "job_description": "description",
    "description_clean": "description",
    "source": "source",
    "search_term": "search_term",
    "search_location": "search_location",
    "source_url": "source_url",
    "scraped_at": "scraped_at",
}


def canonical_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).lower().strip()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def canonical_url(value: object) -> str:
    if pd.isna(value):
        return ""
    raw_text = str(value).strip()
    if not raw_text.lower().startswith(("http://", "https://")):
        return ""
    text = raw_text.lower()
    text = re.sub(r"#.*$", "", text)
    text = re.sub(r"\?.*$", "", text)
    text = re.sub(r"/+$", "", text)
    text = re.sub(r"\s+", "", text)
    if not text:
        return ""
    return text


def text_fingerprint(value: object) -> str:
    text = canonical_text(value)
    if len(text) < MIN_DESCRIPTION_KEY_CHARS:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge raw scraper CSV files into one canonical processed dataset."
    )
    parser.add_argument(
        "--input-dir",
        action="append",
        dest="input_dirs",
        help="Directory to scan recursively for CSV files. Can be provided multiple times.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path. Defaults to {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--include-processed",
        action="store_true",
        help="Also scan Data/processed for candidate CSV inputs.",
    )
    return parser.parse_args()


def project_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(REPO_ROOT, path)


def infer_source_from_name(path: str) -> str:
    name = os.path.basename(path).lower()
    if "glassdoor" in name:
        return "glassdoor"
    if "simply" in name:
        return "simplyhired"
    if "zip" in name:
        return "ziprecruiter"
    if "monster" in name:
        return "monster"
    if "joblist" in name:
        return "joblist"
    if "linkedin" in name:
        return "linkedin"
    return "unknown"


def collect_csv_files(input_dirs: Iterable[str], output_path: str) -> list[str]:
    files: list[str] = []
    seen: set[str] = set()
    output_full_path = os.path.abspath(project_path(output_path))
    for directory in input_dirs:
        directory_full_path = project_path(directory)
        if not os.path.isdir(directory_full_path):
            continue
        pattern = os.path.join(directory_full_path, "**", "*.csv")
        for path in glob.glob(pattern, recursive=True):
            resolved = os.path.abspath(path)
            if resolved == output_full_path:
                continue
            if resolved not in seen:
                files.append(resolved)
                seen.add(resolved)
    return sorted(files)


def normalize_columns(df: pd.DataFrame, path: str) -> pd.DataFrame:
    renamed = df.rename(columns={column: LEGACY_COLUMN_ALIASES.get(column, column) for column in df.columns})

    for column in STANDARD_COLUMNS:
        if column not in renamed.columns:
            renamed[column] = pd.NA

    if renamed["source"].isna().all():
        renamed["source"] = infer_source_from_name(path)

    if renamed["source_url"].isna().all():
        renamed["source_url"] = str(path)

    if renamed["scraped_at"].isna().all():
        renamed["scraped_at"] = pd.Timestamp.now().isoformat(timespec="seconds")

    return renamed[STANDARD_COLUMNS].copy()


def load_and_normalize_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    normalized = normalize_columns(df, path)
    normalized["source_file"] = str(path)
    return normalized


def split_location(value: object) -> tuple[str | None, str | None, str]:
    if pd.isna(value):
        return None, None, "Unknown"

    text = str(value).strip()
    if not text:
        return None, None, "Unknown"

    parts = [part.strip() for part in text.split(",") if part.strip()]
    if len(parts) >= 2:
        city = parts[0]
        state = parts[1]
        return city, state, "United States"
    return text, None, "Unknown"


def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def add_duplicate_keys(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["title_norm"] = df["title"].apply(canonical_text)
    df["company_norm"] = df["company_name"].apply(canonical_text)
    df["location_norm"] = df["job_location"].apply(canonical_text)
    df["description_norm"] = df["description"].apply(canonical_text)
    df["description_hash"] = df["description"].apply(text_fingerprint)
    df["source_url_norm"] = df["source_url"].apply(canonical_url)
    df["strict_identity_key"] = (
        df["title_norm"]
        + "|"
        + df["company_norm"]
        + "|"
        + df["location_norm"]
        + "|"
        + df["description_hash"]
    )
    df.loc[
        df[["title_norm", "company_norm", "location_norm", "description_hash"]].eq("").any(axis=1),
        "strict_identity_key",
    ] = ""
    df["fallback_identity_key"] = df["title_norm"] + "|" + df["company_norm"] + "|" + df["location_norm"]
    df.loc[
        df[["title_norm", "company_norm", "location_norm"]].eq("").any(axis=1),
        "fallback_identity_key",
    ] = ""
    return df


def duplicate_summary(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    candidates = df[df[subset].ne("").all(axis=1)].copy()
    if candidates.empty:
        return candidates
    duplicate_mask = candidates.duplicated(subset=subset, keep=False)
    return candidates.loc[duplicate_mask].sort_values(subset)


def print_duplicate_audit(df: pd.DataFrame) -> None:
    checks = {
        "source_url": ["source_url_norm"],
        "strict_identity": ["strict_identity_key"],
        "fallback_title_company_location": ["fallback_identity_key"],
    }
    for name, subset in checks.items():
        duplicates = duplicate_summary(df, subset)
        if duplicates.empty:
            print(f"Duplicate audit ({name}): 0 duplicate rows")
            continue

        duplicate_groups = duplicates.groupby(subset, dropna=False).ngroups
        print(f"Duplicate audit ({name}): {len(duplicates)} rows across {duplicate_groups} groups")
        preview_columns = ["title", "company_name", "job_location", "source", "source_file"]
        print(duplicates[preview_columns].head(10).to_string(index=False))


def dedupe_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = add_duplicate_keys(df)
    df["completeness"] = (
        df["title_norm"].ne("").astype(int)
        + df["company_norm"].ne("").astype(int)
        + df["location_norm"].ne("").astype(int)
        + df["description_norm"].ne("").astype(int)
        + normalize_text_series(df["salary"]).ne("").astype(int)
    )

    sorted_df = df.sort_values(["completeness", "scraped_at"], ascending=[False, False])
    with_urls = sorted_df[sorted_df["source_url_norm"].ne("")]
    without_urls = sorted_df[sorted_df["source_url_norm"].eq("")]

    deduped = pd.concat(
        [
            with_urls.drop_duplicates(subset=["source_url_norm"], keep="first"),
            without_urls,
        ],
        ignore_index=True,
    )

    with_strict_key = deduped[deduped["strict_identity_key"].ne("")]
    without_strict_key = deduped[deduped["strict_identity_key"].eq("")]
    deduped = pd.concat(
        [
            with_strict_key.drop_duplicates(subset=["strict_identity_key"], keep="first"),
            without_strict_key,
        ],
        ignore_index=True,
    )

    with_fallback_key = deduped[deduped["fallback_identity_key"].ne("")]
    without_fallback_key = deduped[deduped["fallback_identity_key"].eq("")]
    deduped = pd.concat(
        [
            with_fallback_key.drop_duplicates(subset=["fallback_identity_key"], keep="first"),
            without_fallback_key,
        ],
        ignore_index=True,
    )

    deduped = deduped.drop(
        columns=[
            "title_norm",
            "company_norm",
            "location_norm",
            "description_norm",
            "description_hash",
            "source_url_norm",
            "strict_identity_key",
            "fallback_identity_key",
            "completeness",
        ]
    )
    return deduped.reset_index(drop=True)


def assert_no_duplicate_jobs(df: pd.DataFrame) -> None:
    keyed = add_duplicate_keys(df)
    strict_checks = {
        "source_url": ["source_url_norm"],
        "strict_identity": ["strict_identity_key"],
        "fallback_title_company_location": ["fallback_identity_key"],
    }
    failures: list[str] = []
    for name, subset in strict_checks.items():
        duplicates = duplicate_summary(keyed, subset)
        if duplicates.empty:
            continue
        duplicate_groups = duplicates.groupby(subset, dropna=False).ngroups
        preview_columns = ["title", "company_name", "job_location", "source", "source_file"]
        preview = duplicates[preview_columns].head(10).to_string(index=False)
        failures.append(
            f"{name}: {len(duplicates)} duplicate rows across {duplicate_groups} groups\n{preview}"
        )

    if failures:
        message = "\n\n".join(failures)
        raise ValueError(f"Strict duplicate check failed before writing the main CSV:\n{message}")


def build_processed_dataset(df: pd.DataFrame) -> pd.DataFrame:
    processed = df.copy()
    processed["job_title"] = processed["title"]
    processed["job_company"] = processed["company_name"]
    processed["job_schedule_type"] = processed["job_type"]
    processed["Salary"] = processed["salary"]
    processed["description_clean"] = normalize_text_series(processed["description"]).str.lower()

    salary_bounds = processed["Salary"].apply(extract_salary_range)
    processed[["min_salary", "max_salary"]] = salary_bounds
    processed["min_salary"] = processed["min_salary"].apply(normalize_salary)
    processed["max_salary"] = processed["max_salary"].apply(normalize_salary)
    processed["salary_avg"] = processed[["min_salary", "max_salary"]].mean(axis=1)

    processed["has_salary"] = processed["salary_avg"].notna()
    processed["has_description"] = processed["description_clean"].str.strip().ne("")

    location_parts = processed["job_location"].apply(split_location)
    processed["city"] = location_parts.apply(lambda item: item[0])
    processed["state"] = location_parts.apply(lambda item: item[1])
    processed["job_country"] = location_parts.apply(lambda item: item[2])

    processed["skills"] = processed["description_clean"].apply(extract_skills_from_text)
    processed["job_skills"] = processed["skills"].apply(lambda values: values.copy())

    return processed[OUTPUT_COLUMNS].copy()


def main() -> None:
    args = parse_args()

    input_dirs = args.input_dirs or DEFAULT_INPUT_DIRS
    if args.include_processed:
        input_dirs.append("Data/processed")

    files = collect_csv_files(input_dirs, args.output)
    if not files:
        raise SystemExit("No CSV files found in the requested input directories.")

    frames = [load_and_normalize_csv(path) for path in files]
    merged = pd.concat(frames, ignore_index=True)
    keyed_merged = add_duplicate_keys(merged)
    print_duplicate_audit(keyed_merged)

    merged = dedupe_rows(merged)
    assert_no_duplicate_jobs(merged)
    processed = build_processed_dataset(merged)

    output_path = project_path(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    processed.to_csv(output_path, index=False)

    print(f"Merged {len(files)} files into {output_path}")
    print(f"Rows written: {len(processed)}")


if __name__ == "__main__":
    main()
