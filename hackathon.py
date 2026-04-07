import pandas as pd
import re

# Load dataset
df = pd.read_csv("job_dataset.csv", encoding="latin1")

# -----------------------------
# Basic EDA
# -----------------------------
print("Shape:", df.shape)
print("\nColumns:", df.columns)

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset Info:")
print(df.info())

print("\nMissing values:")
print(df.isnull().sum())

print("\nUnique job titles:", df["Title"].nunique())

print("\nExperience levels:")
print(df["ExperienceLevel"].value_counts())

print("\nYears of experience stats:")
print(df["YearsOfExperience"].describe())

print("\nSample skills:")
print(df["Skills"].head(10))


# -----------------------------
# Fill missing values
# -----------------------------
df["Title"] = df["Title"].fillna("")
df["Skills"] = df["Skills"].fillna("")
df["Responsibilities"] = df["Responsibilities"].fillna("")
df["Keywords"] = df["Keywords"].fillna("")
df["ExperienceLevel"] = df["ExperienceLevel"].fillna("")
df["YearsOfExperience"] = df["YearsOfExperience"].fillna("")


# -----------------------------
# Lowercase text columns
# -----------------------------
text_cols = [
    "Title",
    "ExperienceLevel",
    "YearsOfExperience",
    "Skills",
    "Responsibilities",
    "Keywords"
]

for col in text_cols:
    df[col] = df[col].astype(str).str.lower().str.strip()


# -----------------------------
# Clean weird encoding in YearsOfExperience
# -----------------------------
def clean_years_experience(exp):
    exp = str(exp).lower().strip()

    # remove weird encoding characters
    exp = exp.replace("ï¿½", "-")
    exp = exp.replace("�", "-")

    # keep only ascii-safe text
    exp = exp.encode("ascii", "ignore").decode("ascii")

    # remove extra spaces
    exp = exp.strip()

    # common cleanup
    exp = exp.replace("to", "-")
    exp = exp.replace("_", "-")
    exp = exp.replace("--", "-")

    # remove words like years / year / yrs / yr
    exp = re.sub(r"\b(years|year|yrs|yr)\b", "", exp).strip()

    # fix values like "0 - 2"
    exp = re.sub(r"\s*-\s*", "-", exp)

    # cases like "5+"
    plus_match = re.fullmatch(r"(\d+)\+", exp)
    if plus_match:
        return f"{int(plus_match.group(1))}+"

    # normal range like "0-2"
    range_match = re.fullmatch(r"(\d+)-(\d+)", exp)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        if start <= end:
            return f"{start}-{end}"
        else:
            return f"{end}-{start}"

    # single number like "3"
    single_match = re.fullmatch(r"(\d+)", exp)
    if single_match:
        year = int(single_match.group(1))
        return f"{year}-{year}"

    # fix malformed values like "02-mar"
    malformed_prefix = re.match(r"^(\d{1,2})-", exp)
    if malformed_prefix:
        first_num = int(malformed_prefix.group(1))
        if first_num == 0:
            return "0-1"
        elif first_num == 1:
            return "1-2"
        elif first_num == 2:
            return "2-3"
        elif first_num == 3:
            return "3-4"
        elif first_num == 4:
            return "4-5"
        elif first_num >= 5:
            return f"{first_num}+"

    # if nothing matches, fallback
    return "0-1"


df["YearsOfExperience"] = df["YearsOfExperience"].apply(clean_years_experience)


# -----------------------------
# Normalize experience levels
# -----------------------------
def normalize_experience(level):
    level = str(level).lower().strip()

    if "entry" in level or "fresher" in level or "junior" in level:
        return "entry"
    elif "mid" in level:
        return "mid"
    elif "senior" in level or "lead" in level:
        return "senior"
    elif "experienced" in level:
        return "experienced"
    else:
        return level


df["ExperienceLevel"] = df["ExperienceLevel"].apply(normalize_experience)


# -----------------------------
# Remove duplicates before list column
# -----------------------------
df = df.drop_duplicates()


# -----------------------------
# Clean skills column
# -----------------------------
def clean_skills(skill_text):
    return [skill.strip().lower() for skill in str(skill_text).split(";") if skill.strip()]


df["Skills_List"] = df["Skills"].apply(clean_skills)


# -----------------------------
# Create combined text
# -----------------------------
df["combined_text"] = (
    df["Title"] + " " +
    df["Skills"] + " " +
    df["Responsibilities"] + " " +
    df["Keywords"]
)


# -----------------------------
# Final check
# -----------------------------
print("\nCleaned YearsOfExperience sample:")
print(df["YearsOfExperience"].head(20))

print("\nFinal dataset shape:", df.shape)
print(df[["Title", "ExperienceLevel", "YearsOfExperience", "Skills_List", "combined_text"]].head())


# -----------------------------
# Save cleaned data
# -----------------------------
df.to_csv("cleaned_jobs.csv", index=False)
print("\nCleaned dataset saved as cleaned_jobs.csv")