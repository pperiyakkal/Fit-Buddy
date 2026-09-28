from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import (
    SessionLocal,
    delete_user,
    get_all_users,
    get_original_plan,
    get_plan,
    get_user,
    get_user_plan_map,
    save_plan,
    save_user,
    update_plan,
)
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "FitBuddy | AI Fitness Planner"},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "FitBuddy | Validation Error",
                "error": str(exc),
                "form_data": {
                    "username": username,
                    "user_id": user_id,
                    "age": age,
                    "weight": weight,
                    "goal": goal,
                    "intensity": intensity,
                },
            },
            status_code=422,
        )

    plan = generate_workout_gemini(user)
    tip = generate_nutrition_tip_with_flash(user)

    save_user(
        db,
        user_id=user.user_id,
        username=user.username,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )
    save_plan(
        db,
        user_id=user.user_id,
        original_plan=plan,
        nutrition_tip=tip,
    )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "FitBuddy | Your Plan",
            "user": user,
            "workout_plan": plan,
            "nutrition_tip": tip,
            "updated": False,
        },
    )


@router.get("/result/{user_id}", response_class=HTMLResponse)
def result_page(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
):
    db_user = get_user(db, user_id)
    db_plan = get_plan(db, user_id)
    if not db_user or not db_plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    user = UserInput(
        username=db_user.username,
        user_id=db_user.user_id,
        age=db_user.age,
        weight=db_user.weight,
        goal=db_user.goal,
        intensity=db_user.intensity,
    )
    displayed_plan = db_plan.updated_plan or db_plan.original_plan
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "FitBuddy | Your Plan",
            "user": user,
            "workout_plan": displayed_plan,
            "nutrition_tip": db_plan.nutrition_tip,
            "updated": bool(db_plan.updated_plan),
        },
    )


@router.get("/feedback/{user_id}", response_class=HTMLResponse)
def feedback_page(request: Request, user_id: str, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return templates.TemplateResponse(
        request=request,
        name="feedback.html",
        context={
            "title": "FitBuddy | Update Plan",
            "user_id": user_id,
            "username": db_user.username,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    return _process_feedback(request, user_id, feedback, db)


def _process_feedback(
    request: Request,
    user_id: str,
    feedback: str,
    db: Session,
):
    db_user = get_user(db, user_id)
    original = get_original_plan(db, user_id)
    if not db_user or not original:
        raise HTTPException(status_code=404, detail="User or original plan not found.")

    user = UserInput(
        username=db_user.username,
        user_id=db_user.user_id,
        age=db_user.age,
        weight=db_user.weight,
        goal=db_user.goal,
        intensity=db_user.intensity,
    )
    feedback_request = FeedbackRequest(user_id=user_id, feedback=feedback)
    revised = update_workout_plan(user, original, feedback_request.feedback)
    current = get_plan(db, user_id)
    updated_tip = current.nutrition_tip if current else ""

    update_plan(
        db,
        user_id=user_id,
        updated_plan=revised,
        feedback=feedback_request.feedback,
        nutrition_tip=updated_tip,
    )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "FitBuddy | Updated Plan",
            "user": user,
            "workout_plan": revised,
            "nutrition_tip": updated_tip,
            "updated": True,
            "feedback": feedback_request.feedback,
        },
    )


@router.post("/api/generate-workout")
def api_generate_workout(
    payload: UserInput,
    db: Session = Depends(get_db),
):
    plan = generate_workout_gemini(payload)
    tip = generate_nutrition_tip_with_flash(payload)
    save_user(
        db,
        user_id=payload.user_id,
        username=payload.username,
        age=payload.age,
        weight=payload.weight,
        goal=payload.goal,
        intensity=payload.intensity,
    )
    save_plan(
        db,
        user_id=payload.user_id,
        original_plan=plan,
        nutrition_tip=tip,
    )
    return {
        "message": "Workout plan generated successfully.",
        "user": payload.model_dump(),
        "workout_plan": plan,
        "nutrition_tip": tip,
    }


@router.post("/api/submit-feedback")
def api_submit_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    db_user = get_user(db, payload.user_id)
    original = get_original_plan(db, payload.user_id)
    if not db_user or not original:
        raise HTTPException(status_code=404, detail="User or original plan not found.")

    user = UserInput(
        username=db_user.username,
        user_id=db_user.user_id,
        age=db_user.age,
        weight=db_user.weight,
        goal=db_user.goal,
        intensity=db_user.intensity,
    )
    revised = update_workout_plan(user, original, payload.feedback)
    plan = update_plan(
        db,
        user_id=payload.user_id,
        updated_plan=revised,
        feedback=payload.feedback,
    )
    return {
        "message": "Workout plan updated successfully.",
        "user_id": payload.user_id,
        "updated_plan": plan.updated_plan if plan else revised,
    }


@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    plan_map = get_user_plan_map(db)
    return {
        "users": [
            {
                "user_id": user.user_id,
                "username": user.username,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "created_at": user.created_at.isoformat(),
                "has_updated_plan": bool(
                    plan_map.get(user.user_id)
                    and plan_map[user.user_id].updated_plan
                ),
            }
            for user in users
        ]
    }


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    plan_map = get_user_plan_map(db)
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "title": "FitBuddy | All Users",
            "users": users,
            "plan_map": plan_map,
        },
    )


@router.post("/delete-user/{user_id}")
def delete_user_route(user_id: str, db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)
