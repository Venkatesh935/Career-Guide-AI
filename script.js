const API_URL = "http://127.0.0.1:5000/recommend";

const recommendForm = document.getElementById("recommendForm");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const resultsSection = document.getElementById("resultsSection");
const resultsContainer = document.getElementById("resultsContainer");

recommendForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  errorBox.classList.add("hidden");
  resultsSection.classList.add("hidden");
  resultsContainer.innerHTML = "";
  loading.classList.remove("hidden");

  const skillsInput = document.getElementById("skills").value.trim();
  const experienceLevel = document.getElementById("experienceLevel").value;
  const yearsOfExperience = parseFloat(document.getElementById("yearsOfExperience").value);
  const topN = parseInt(document.getElementById("topN").value);

  const skills = skillsInput
    .split(",")
    .map(skill => skill.trim())
    .filter(skill => skill !== "");

  if (skills.length === 0) {
    showError("Please enter at least one skill.");
    loading.classList.add("hidden");
    return;
  }

  if (experienceLevel === "senior" && yearsOfExperience < 5) {
  showError("Senior level requires at least 5 years of experience");
  return;
}

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        skills: skills,
        experience_level: experienceLevel,
        years_of_experience: yearsOfExperience,
        top_n: topN
      })
    });

    const data = await response.json();

    loading.classList.add("hidden");

    if (!response.ok) {
      showError(data.error || "Something went wrong.");
      return;
    }

    displayResults(data.recommendations);
  } catch (error) {
    loading.classList.add("hidden");
    showError("Unable to connect to backend. Make sure Flask server is running.");
    console.error(error);
  }
});

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function displayResults(recommendations) {
  if (!recommendations || recommendations.length === 0) {
    showError("No recommendations found.");
    return;
  }

  resultsSection.classList.remove("hidden");

  recommendations.forEach((job, index) => {
    const card = document.createElement("div");
    card.className = "result-card";

    const matchPercentage = Math.round((job.final_score || 0) * 100);

    card.innerHTML = `
      <h3>${index + 1}. ${job.title}</h3>

      <div class="result-meta">
        <span class="badge">Job ID: ${job.job_id}</span>
        <span class="badge">Level: ${job.experience_level}</span>
        <span class="badge">Required Years: ${job.years_of_experience}</span>
        <span class="badge">Match: ${matchPercentage}%</span>
      </div>

      <div class="score-box">
        <p><strong>Final Score:</strong> ${job.final_score}</p>
        <p><strong>Cosine Score:</strong> ${job.cosine_score}</p>
        <p><strong>Skill Overlap:</strong> ${job.skill_overlap_score}</p>
        <p><strong>Experience Level Score:</strong> ${job.experience_match_score}</p>
        <p><strong>Years Experience Score:</strong> ${job.years_experience_match_score}</p>
      </div>

      <div class="skills-section">
        <h4>Matched Skills</h4>
        <div class="skill-list">
          ${
            job.matched_skills && job.matched_skills.length > 0
              ? job.matched_skills.map(skill => `<span class="skill-tag match-tag">${skill}</span>`).join("")
              : `<span class="skill-tag">No matched skills</span>`
          }
        </div>
      </div>

      <div class="skills-section">
        <h4>Missing Skills</h4>
        <div class="skill-list">
          ${
            job.missing_skills && job.missing_skills.length > 0
              ? job.missing_skills.slice(0, 8).map(skill => `<span class="skill-tag missing-tag">${skill}</span>`).join("")
              : `<span class="skill-tag">No missing skills</span>`
          }
        </div>
      </div>
    `;

    resultsContainer.appendChild(card);
  });
}