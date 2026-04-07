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
    .map(skill => skill.trim().toLowerCase())
    .filter(skill => skill !== "");

  if (skills.length === 0) {
    showError("Please enter at least one skill.");
    loading.classList.add("hidden");
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
      <div class="result-top">
        <div class="job-title-box">
          <h3>${index + 1}. ${job.title}</h3>
          <p class="job-id">Job ID: ${job.job_id}</p>
        </div>

        <div class="match-box">
          <div class="match-label">Overall Match</div>
          <div class="match-value">${matchPercentage}%</div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${matchPercentage}%"></div>
          </div>
        </div>
      </div>

      <div class="meta-row">
        <span class="meta-badge">Level: ${job.experience_level}</span>
        <span class="meta-badge">Required Years: ${job.years_of_experience}</span>
      </div>

      <div class="score-grid">
        <div class="score-item">
          <h4>Final Score</h4>
          <p>${job.final_score}</p>
        </div>
        <div class="score-item">
          <h4>Cosine Score</h4>
          <p>${job.cosine_score}</p>
        </div>
        <div class="score-item">
          <h4>Skill Overlap</h4>
          <p>${job.skill_overlap_score}</p>
        </div>
        <div class="score-item">
          <h4>Years Match</h4>
          <p>${job.years_experience_match_score}</p>
        </div>
      </div>

      <div class="skills-wrapper">
        <div class="skill-block">
          <h4>Matched Skills</h4>
          <div class="skill-list">
            ${
              job.matched_skills && job.matched_skills.length > 0
                ? job.matched_skills.map(skill => `<span class="skill-tag match-tag">${skill}</span>`).join("")
                : `<span class="skill-tag empty-tag">No matched skills</span>`
            }
          </div>
        </div>

        <div class="skill-block">
          <h4>Missing Skills</h4>
          <div class="skill-list">
            ${
              job.missing_skills && job.missing_skills.length > 0
                ? job.missing_skills.slice(0, 10).map(skill => `<span class="skill-tag missing-tag">${skill}</span>`).join("")
                : `<span class="skill-tag empty-tag">No missing skills</span>`
            }
          </div>
        </div>
      </div>
    `;

    resultsContainer.appendChild(card);
  });
}
