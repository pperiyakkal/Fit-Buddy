from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai

from .schemas import UserInput

load_dotenv()

TIP_MODEL = os.getenv("GEMINI_TIP_MODEL", "gemini-3.8-flash")


def _demo_tip(goal: str) -> str:
    tips = {
        "weight loss": "Build meals around vegetables, a protein source, whole-food carbohydrates as appropriate, and water. Aim for sustainable habits rather than extreme restriction.",
        "muscle gain": "Include a protein source in each main meal and support training with adequate overall food, hydration, and recovery.",
        "general wellness": "Prioritize regular hydration, balanced meals, sufficient sleep, and a consistent mix of strength, cardio, and mobility work.",
        "flexibility": "Stay hydrated and include protein-rich foods and a varied diet while giving your body enough recovery between mobility sessions.",
    }
    return tips.get(goal, tips["general wellness"])


def generate_nutrition_tip_with_flash(user: UserInput) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.lower().startswith("your_"):
        return _demo_tip(user.goal)

    client = genai.Client(api_key=api_key)
    prompt = f"""
Give one concise, practical nutrition or recovery tip for a person whose fitness goal is "{user.goal}".
Their preferred workout intensity is "{user.intensity}".
Keep it general wellness information, not medical advice.
Avoid calorie prescriptions, supplement prescriptions, or extreme diets.
Return 2–4 sentences.
"""
    response = client.models.generate_content(
        model=TIP_MODEL,
        contents=prompt,
    )
    return (response.text or "").strip() or _demo_tip(user.goal)
