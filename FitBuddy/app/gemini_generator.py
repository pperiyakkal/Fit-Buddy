from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai

from .schemas import UserInput

load_dotenv()

WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.8-flash")


def _demo_plan(user: UserInput) -> str:
    intensity = user.intensity.title()
    return f"""FITBUDDY 7-DAY WORKOUT PLAN
Name: {user.username}
Goal: {user.goal.title()}
Intensity: {intensity}

Day 1 – Full Body Foundation
Warm-up: 8 minutes brisk walking + dynamic mobility.
Main: Squats 3x10, incline push-ups 3x8, rows 3x10, glute bridges 3x12.
Cooldown: 5 minutes easy stretching.

Day 2 – Cardio + Core
Warm-up: 5 minutes easy movement.
Main: 25-minute moderate cardio; dead bug 3x10/side; plank 3x20–30 sec.
Cooldown: 5 minutes relaxed walking.

Day 3 – Recovery & Mobility
Warm-up: 5 minutes gentle walking.
Main: 20–30 minutes mobility/yoga; light stretching for hips, shoulders and back.
Recovery: Hydrate and prioritize sleep.

Day 4 – Lower Body
Warm-up: 8 minutes.
Main: Squats 3x10, reverse lunges 3x8/side, hip hinges 3x10, calf raises 3x15.
Cooldown: 5–8 minutes.

Day 5 – Upper Body + Core
Warm-up: 8 minutes.
Main: Push-ups 3x8–12, rows 3x10, shoulder press 3x10, bird-dog 3x10/side.
Cooldown: 5 minutes.

Day 6 – Goal-Focused Conditioning
Warm-up: 8 minutes.
Main: 20–30 minutes goal-appropriate cardio/conditioning at a sustainable effort.
Cooldown: 5–10 minutes.

Day 7 – Rest / Active Recovery
Easy walking and gentle mobility only.
Recovery focus: hydration, sleep and preparing for the next week.

Intensity note: {intensity}. Start conservatively and adjust volume to your experience and recovery."""


def generate_workout_gemini(user: UserInput) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.lower().startswith("your_"):
        return _demo_plan(user)

    client = genai.Client(api_key=api_key)
    prompt = f"""
You are FitBuddy, a careful general fitness-planning assistant.
Create a structured 7-day workout plan for:
Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Preferred intensity: {user.intensity}

Requirements:
- Seven clearly labeled days.
- For training days include warm-up, main exercises, sets/reps or duration, rest guidance, and cooldown/recovery.
- Include at least one recovery/rest day.
- Match the requested goal and intensity.
- Keep recommendations general and beginner-friendly unless the user information supports more.
- Do not diagnose medical conditions or prescribe treatment.
- Include a short safety note: stop if pain, dizziness, or concerning symptoms occur and seek professional guidance.
- Do not claim that the plan is medically personalized.
- Use plain text with clear headings. Do not use markdown tables.
"""
    response = client.models.generate_content(
        model=WORKOUT_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip() or _demo_plan(user)
