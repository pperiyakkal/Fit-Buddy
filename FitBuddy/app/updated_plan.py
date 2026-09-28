from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai

from .gemini_generator import WORKOUT_MODEL
from .schemas import UserInput

load_dotenv()


def _demo_update(original_plan: str, feedback: str, user: UserInput) -> str:
    return f"""UPDATED FITBUDDY PLAN
Goal: {user.goal.title()}
Intensity: {user.intensity.title()}

User feedback incorporated:
{feedback}

The original plan has been adjusted by emphasizing the requested preference while preserving a recovery day.

{original_plan}

Update note:
- Apply the feedback gradually rather than increasing training volume abruptly.
- Keep at least one recovery-focused day.
- Stop if an exercise causes pain or concerning symptoms and seek appropriate professional guidance."""


def update_workout_plan(
    user: UserInput,
    original_plan: str,
    feedback: str,
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.lower().startswith("your_"):
        return _demo_update(original_plan, feedback, user)

    client = genai.Client(api_key=api_key)
    prompt = f"""
You are FitBuddy updating a general fitness plan.

User:
Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Original plan:
{original_plan}

User feedback:
{feedback}

Create a revised 7-day plan that incorporates the feedback where reasonable.
Preserve the user's goal and preferred intensity.
Include warm-ups, main work, recovery/cooldown guidance, and at least one rest/recovery day.
Do not provide medical diagnosis or treatment. Do not claim clinical personalization.
Add a short safety note.
Return clear plain text headings and no markdown table.
"""
    response = client.models.generate_content(
        model=WORKOUT_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip() or _demo_update(original_plan, feedback, user)
