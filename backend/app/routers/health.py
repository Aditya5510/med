from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import json
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any
import traceback
import sys
from ..dependencies import get_database
from ..models.schemas import (
    HealthProfileCreate,
    HealthProfileResponse,
    HealthProfileInDB,
    MealPlanResponse,
    MealPlanDay,
    UserInDB,
)
from ..routers.auth import get_current_user
from ..tools.bmr_calculator import calculate_bmr
from ..tools.meal_planner import generate_meal_plan
from ..tools.workout_generator import generate_workout_plan
from ..models.schemas import WorkoutPlanResponse, WorkoutPlanDay, ExerciseItem
from ..tools.recipe_fetcher import fetch_recipe
from ..models.schemas import RecipeResponse
from ..tools.push_notifier import send_push_notification
from ..models.schemas import UserResponse
from ..lmm_client import ask_llm

router = APIRouter()

@router.get("/ping")
async def ping(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Simple endpoint to verify the service and database connection.
    """
    collections = await db.list_collection_names()
    return {"status": "alive", "collections": collections}


@router.post(
    "/profile",
    response_model=HealthProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_profile(
    profile_in: HealthProfileCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Create or update the health profile for the currently authenticated user.
    If a profile already exists, update it; otherwise, insert a new one.
    """
    user_id_str = current_user.id

    if not ObjectId.is_valid(user_id_str):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    existing = await db["health_profiles"].find_one({"user_id": user_id_str})
    now = datetime.utcnow()
    profile_data = {
        "age": profile_in.age,
        "gender": profile_in.gender,
        "weight": profile_in.weight,
        "height": profile_in.height,
        "dietary_preferences": profile_in.dietary_preferences or [],
        "existing_conditions": profile_in.existing_conditions or [],
        "user_id": user_id_str,
        "updated_at": now,
    }

    if existing:
        # Update existing document
        await db["health_profiles"].update_one(
            {"_id": existing["_id"]},
            {"$set": profile_data}
        )
        updated = await db["health_profiles"].find_one({"_id": existing["_id"]})
        return HealthProfileResponse(
            age=updated["age"],
            gender=updated["gender"],
            weight=updated["weight"],
            height=updated["height"],
            dietary_preferences=updated.get("dietary_preferences", []),
            existing_conditions=updated.get("existing_conditions", []),
            created_at=updated["created_at"],
            updated_at=updated["updated_at"],
        )
    else:
        # Insert a new document
        profile_data["created_at"] = now
        result = await db["health_profiles"].insert_one(profile_data)
        inserted = await db["health_profiles"].find_one({"_id": result.inserted_id})
        return HealthProfileResponse(
            age=inserted["age"],
            gender=inserted["gender"],
            weight=inserted["weight"],
            height=inserted["height"],
            dietary_preferences=inserted.get("dietary_preferences", []),
            existing_conditions=inserted.get("existing_conditions", []),
            created_at=inserted["created_at"],
            updated_at=inserted["updated_at"],
        )


@router.get(
    "/profile",
    response_model=HealthProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def read_profile(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get the health profile of the currently authenticated user.
    Returns 404 if no profile exists.
    """
    user_id_str = current_user.id

    if not ObjectId.is_valid(user_id_str):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    existing = await db["health_profiles"].find_one({"user_id": user_id_str})
    if not existing:
        raise HTTPException(status_code=404, detail="Health profile not found")

    return HealthProfileResponse(
        age=existing["age"],
        gender=existing["gender"],
        weight=existing["weight"],
        height=existing["height"],
        dietary_preferences=existing.get("dietary_preferences", []),
        existing_conditions=existing.get("existing_conditions", []),
        created_at=existing["created_at"],
        updated_at=existing["updated_at"],
    )


@router.get(
    "/profile/bmr",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_bmr(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Compute and return the BMR for the current user's stored profile.
    If no profile exists, return 404.
    """
    user_id_str = current_user.id

    existing = await db["health_profiles"].find_one({"user_id": user_id_str})
    if not existing:
        raise HTTPException(status_code=404, detail="Health profile not found")

    age = existing["age"]
    gender = existing["gender"]
    weight = existing["weight"]
    height = existing["height"]

    bmr_value = calculate_bmr(age=age, weight=weight, height=height, gender=gender)
    return {"bmr": bmr_value}



@router.post(
    "/mealplan",
    response_model=MealPlanResponse,
    status_code=status.HTTP_200_OK,
)
async def create_meal_plan(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    user_id_str = current_user.id

    existing = await db["health_profiles"].find_one({"user_id": user_id_str})
    if not existing:
        raise HTTPException(status_code=404, detail="Health profile not found")

    age = existing["age"]
    gender = existing["gender"]
    weight = existing["weight"]
    height = existing["height"]
    bmr_value = calculate_bmr(age=age, weight=weight, height=height, gender=gender)

    calorie_target = round(bmr_value * 1.2, 2)

    dietary_preferences = existing.get("dietary_preferences", [])
    plan_list = generate_meal_plan(
        calorie_target=calorie_target,
        dietary_pref=dietary_preferences,
        days=7
    )

    days_response = [MealPlanDay(day=day["day"], meals=day["meals"]) for day in plan_list]

    return MealPlanResponse(
        calorie_target=calorie_target,
        days=days_response
    )    


########################################

@router.post(
    "/workoutplan",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_200_OK,
)
async def create_workout_plan(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    user_id_str = current_user.id

    # 1. Fetch profile
    existing = await db["health_profiles"].find_one({"user_id": user_id_str})
    if not existing:
        raise HTTPException(status_code=404, detail="Health profile not found")

    existing_conditions = existing.get("existing_conditions", [])

    plan_list = generate_workout_plan(existing_conditions=existing_conditions, days=7)

    days_response = []
    for day_dict in plan_list:
        exercises_items = [
            ExerciseItem(name=ex["name"], reps=ex.get("reps"), duration=ex.get("duration"))
            for ex in day_dict["exercises"]
        ]
        days_response.append(WorkoutPlanDay(day=day_dict["day"], exercises=exercises_items))

    return WorkoutPlanResponse(days=days_response)



#########################################################

@router.get(
    "/recipe/{meal_name}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_recipe(
    meal_name: str,
    current_user: UserInDB = Depends(get_current_user),
):

    recipe_data = fetch_recipe(meal_name)
    return RecipeResponse(**recipe_data)



#######################

@router.post(
    "/notify",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
)
async def notify_now(
    payload: Dict[str, str],  # expects {"message": "..."}
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Trigger a push notification for the current user immediately.
    Body: { "message": "Your custom reminder text" }
    """
    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    user_id_str = current_user.id

    # Call our stub tool
    result = send_push_notification(user_id=user_id_str, message=message)
    return result





############################################### 

LLM_ORCHESTRATOR_PROMPT = """
You are an orchestrator. Output ONLY valid JSON with no extra text or markdown fences.

Available tools:
1. calculate_bmr(age: int, weight: float, height: float, gender: str) -> {{ "bmr": float }}
2. generate_meal_plan(calorie_target: float, dietary_pref: List[str], days: int) -> [ … ]
3. generate_workout_plan(goal: str, days_per_week: int, conditions: List[str]) -> [ … ]
4. fetch_recipe(meal_name: str) -> {{ … }}

Return a single JSON object with a top‐level key "steps" whose value is a list of:
  {{ "tool": "<tool_name>", "args": {{ … }} }}

Do NOT output any fences or commentary—only the JSON.

User profile:
  age: {{age}}
  weight: {{weight}}
  height: {{height}}
  gender: "{{gender}}"
  dietary_preferences: {{dietary_preferences}}
  existing_conditions: {{existing_conditions}}

User’s goal:
  "{{goal}}"
"""

def clean_llm_output(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = raw.splitlines()
        cleaned = []
        for line in lines:
            if line.strip().startswith("```"):
                continue
            cleaned.append(line)
        return "\n".join(cleaned).strip()
    return raw

async def orchestrate_plan(
    db: AsyncIOMotorDatabase, user: UserInDB, goal: str
) -> Dict[str, Any]:
    prof = await db["health_profiles"].find_one({"user_id": user.id})
    if not prof:
        raise HTTPException(status_code=404, detail="Health profile not found")

    age = prof["age"]
    weight = prof["weight"]
    height = prof["height"]
    gender = prof["gender"]
    dietary_preferences = prof.get("dietary_preferences", [])
    existing_conditions = prof.get("existing_conditions", [])

    prompt = LLM_ORCHESTRATOR_PROMPT.format(
        age=age,
        weight=weight,
        height=height,
        gender=gender,
        dietary_preferences=dietary_preferences,
        existing_conditions=existing_conditions,
        goal=goal.replace('"', '\\"'),
    )

    llm_output = ask_llm(prompt)
    print("⏺ LLM raw output:\n", llm_output, file=sys.stderr)

    llm_clean = clean_llm_output(llm_output)
    try:
        doc = json.loads(llm_clean)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"LLM returned invalid JSON:\n{llm_output}"
        )

    steps = doc.get("steps", [])
    result: Dict[str, Any] = {}

    for step in steps:
        tool_name = step.get("tool")
        args = step.get("args", {})

        if tool_name == "calculate_bmr":
            b = calculate_bmr(
                age=args["age"],
                weight=args["weight"],
                height=args["height"],
                gender=args["gender"],
            )
            result["bmr"] = b

        elif tool_name == "generate_meal_plan":
            mp = generate_meal_plan(
                calorie_target=args["calorie_target"],
                dietary_pref=args["dietary_pref"],
                days=args["days"],
            )
            result["meal_plan"] = mp

        elif tool_name == "generate_workout_plan":
            wp = generate_workout_plan(
                goal=args["goal"],
                days_per_week=args["days_per_week"],
                conditions=args["conditions"],
            )
            result["workout_plan"] = wp    

        elif tool_name == "fetch_recipe":
         
            meal_name = args.get("meal_name", "")
            if not meal_name:
                raise HTTPException(status_code=400, detail="fetch_recipe requires meal_name")
            recipe = fetch_recipe(meal_name=meal_name)
           
            result.setdefault("recipes", []).append(recipe)

        else:
            raise HTTPException(status_code=500, detail=f"Unknown tool: {tool_name}")

    return result

@router.post(
    "/plan",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
)
async def create_full_plan(
    payload: Dict[str, str],
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_user),
):
    goal = payload.get("goal", "").strip()
    if not goal:
        raise HTTPException(status_code=400, detail="Goal is required")

    try:
        plan = await orchestrate_plan(db, current_user, goal)
        return plan
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
