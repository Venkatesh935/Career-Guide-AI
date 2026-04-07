import pandas as pd
import ast
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load cleaned dataset
df = pd.read_csv("cleaned_jobs.csv")

# Convert Skills_List back to Python list
def parse_skills_list(x):
    if isinstance(x, list):
        return x
    if pd.isna(x):
        return []
    try:
        return ast.literal_eval(x)
    except:
        return [skill.strip().lower() for skill in str(x).split(";") if skill.strip()]

df["Skills_List"] = df["Skills_List"].apply(parse_skills_list)

# Fill missing values
df["combined_text"] = df["combined_text"].fillna("")
df["ExperienceLevel"] = df["ExperienceLevel"].fillna("")
df["YearsOfExperience"] = df["YearsOfExperience"].fillna("")
df["Title"] = df["Title"].fillna("")
df["JobID"] = df["JobID"].fillna("")

# TF-IDF
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["combined_text"])


def clean_input_skills(skills):
    return [skill.strip().lower() for skill in skills if skill and skill.strip()]


def skill_overlap_score(user_skills, job_skills):
    if not job_skills:
        return 0.0

    user_skills_set = set(skill.lower() for skill in user_skills)
    job_skills_set = set(skill.lower() for skill in job_skills)
    matched = user_skills_set.intersection(job_skills_set)

    return len(matched) / len(job_skills_set)


def get_matched_skills(user_skills, job_skills):
    user_skills_set = set(skill.lower() for skill in user_skills)
    job_skills_set = set(skill.lower() for skill in job_skills)
    return sorted(list(user_skills_set.intersection(job_skills_set)))


def get_missing_skills(user_skills, job_skills):
    user_skills_set = set(skill.lower() for skill in user_skills)
    job_skills_set = set(skill.lower() for skill in job_skills)
    return sorted(list(job_skills_set - user_skills_set))


def normalize_user_experience(level):
    level = str(level).lower().strip()

    if "fresher" in level or "entry" in level or "junior" in level:
        return "entry"
    elif "mid" in level:
        return "mid"
    elif "senior" in level or "lead" in level:
        return "senior"
    elif "experienced" in level:
        return "experienced"
    else:
        return level


def experience_match_score(user_level, job_level):
    user_level = normalize_user_experience(user_level)
    job_level = str(job_level).lower().strip()

    if user_level == job_level:
        return 1.0

    close_matches = {
        "entry": ["experienced"],
        "mid": ["experienced", "senior"],
        "experienced": ["entry", "mid", "senior"],
        "senior": ["experienced", "mid"]
    }

    if user_level in close_matches and job_level in close_matches[user_level]:
        return 0.5

    return 0.0


def extract_experience_range(exp_text):
    """
    Convert job experience text into min and max years.
    Examples:
    '0-1' -> (0, 1)
    '2-4' -> (2, 4)
    '5+'  -> (5, 100)
    '3 years' -> (3, 3)
    """
    exp_text = str(exp_text).lower().strip()

    range_match = re.search(r"(\d+)\s*-\s*(\d+)", exp_text)
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2))

    plus_match = re.search(r"(\d+)\s*\+", exp_text)
    if plus_match:
        return int(plus_match.group(1)), 100

    single_match = re.search(r"(\d+)", exp_text)
    if single_match:
        year = int(single_match.group(1))
        return year, year

    return 0, 100


def years_experience_match_score(user_years, job_years_text):
    """
    Returns score between 0 and 1
    """
    try:
        user_years = float(user_years)
    except:
        return 0.0

    min_years, max_years = extract_experience_range(job_years_text)

    if min_years <= user_years <= max_years:
        return 1.0

    # near match: 1 year below or above
    if user_years == min_years - 1 or user_years == max_years + 1:
        return 0.5

    return 0.0


def recommend_jobs(user_skills, user_experience_level, user_years_of_experience, top_n=5):
    user_skills = clean_input_skills(user_skills)
    user_experience_level = normalize_user_experience(user_experience_level)

    user_text = " ".join(user_skills) + " " + user_experience_level
    user_vector = vectorizer.transform([user_text])

    cosine_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    recommendations = []

    for i, row in df.iterrows():
        job_skills = row["Skills_List"]

        overlap = skill_overlap_score(user_skills, job_skills)
        exp_level_score = experience_match_score(user_experience_level, row["ExperienceLevel"])
        exp_years_score = years_experience_match_score(user_years_of_experience, row["YearsOfExperience"])

        final_score = (
            0.5 * cosine_scores[i] +
            0.25 * overlap +
            0.10 * exp_level_score +
            0.15 * exp_years_score
        )

        recommendations.append({
            "job_id": str(row["JobID"]),
            "title": str(row["Title"]),
            "experience_level": str(row["ExperienceLevel"]),
            "years_of_experience": str(row["YearsOfExperience"]),
            "final_score": round(float(final_score), 4),
            "cosine_score": round(float(cosine_scores[i]), 4),
            "skill_overlap_score": round(float(overlap), 4),
            "experience_match_score": round(float(exp_level_score), 4),
            "years_experience_match_score": round(float(exp_years_score), 4),
            "matched_skills": get_matched_skills(user_skills, job_skills),
            "missing_skills": get_missing_skills(user_skills, job_skills)
        })

    recommendations = sorted(recommendations, key=lambda x: x["final_score"], reverse=True)
    return recommendations[:top_n]


if __name__ == "__main__":
    user_skills = ["c#", ".net", "asp.net", "sql server", "html", "css"]
    user_experience_level = "fresher"
    user_years_of_experience = 1

    results = recommend_jobs(
        user_skills,
        user_experience_level,
        user_years_of_experience,
        top_n=5
    )

    print("\nTop Job Recommendations:\n")

    for idx, job in enumerate(results, start=1):
        print(f"Rank {idx}")
        print("Job ID:", job["job_id"])
        print("Title:", job["title"])
        print("Experience Level:", job["experience_level"])
        print("Years of Experience:", job["years_of_experience"])
        print("Final Score:", job["final_score"])
        print("Cosine Score:", job["cosine_score"])
        print("Skill Overlap Score:", job["skill_overlap_score"])
        print("Experience Level Match Score:", job["experience_match_score"])
        print("Years Experience Match Score:", job["years_experience_match_score"])
        print("Matched Skills:", ", ".join(job["matched_skills"]) if job["matched_skills"] else "None")
        print("Missing Skills:", ", ".join(job["missing_skills"][:5]) if job["missing_skills"] else "None")
        print("-" * 50)