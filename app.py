from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend_jobs

app = Flask(__name__)
CORS(app)

def validate_experience(experience_level, years):
    experience_level = str(experience_level).lower()

    if experience_level in ["fresher", "entry"]:
       return 0 <= years <= 1

    elif experience_level == "mid":
         return 2 <= years <= 5

    elif experience_level == "experienced":
         return 3 <= years <= 7

    elif experience_level == "senior":
         return years >= 5

    return True

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Job Recommendation API is running"
    })


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        skills = data.get("skills", [])
        experience_level = data.get("experience_level", "")
        years_of_experience = data.get("years_of_experience", 0)
        top_n = data.get("top_n", 5)

        if not isinstance(skills, list) or len(skills) == 0:
            return jsonify({"error": "skills must be a non-empty list"}), 400

        if not experience_level:
            return jsonify({"error": "experience_level is required"}), 400

        try:
            years_of_experience = float(years_of_experience)
        except:
            return jsonify({"error": "years_of_experience must be a number"}), 400
        
        if not validate_experience(experience_level, years_of_experience):
            return jsonify({"error": f"Invalid combination: {experience_level} level cannot have {years_of_experience} years of experience"}), 400

        results = recommend_jobs(skills, experience_level, years_of_experience, top_n)

        return jsonify({
            "user_input": {
                "skills": skills,
                "experience_level": experience_level,
                "years_of_experience": years_of_experience,
                "top_n": top_n
            },
            "recommendations": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)