function copyPlan(){
  const el = document.getElementById("workout-plan");
  if (!el) return;
  navigator.clipboard.writeText(el.innerText)
    .then(() => alert("Workout plan copied."))
    .catch(() => alert("Copy failed. You can select the plan manually."));
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("plan-form");
  if (form) {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[type=submit]");
      if (button) {
        button.disabled = true;
        button.textContent = "Generating plan…";
      }
    });
  }
});
