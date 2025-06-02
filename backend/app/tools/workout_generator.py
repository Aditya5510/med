from typing import List, Dict, Any

def generate_workout_plan(
    goal: str,
    days_per_week: int,
    conditions: List[str],
) -> List[Dict[str, Any]]:

    base_exercises = []
    if "knee pain" in conditions:
        base_exercises = [
            {"name": "Push-Ups", "reps": "3x12", "rest": "60s"},
            {"name": "Seated Leg Extensions", "reps": "3x15", "rest": "45s"},
        ]
    else:
        base_exercises = [
            {"name": "Push-Ups", "reps": "3x12", "rest": "60s"},
            {"name": "Bodyweight Squats", "reps": "3x15", "rest": "60s"},
        ]

  
    if "lose weight" in goal.lower():
        base_exercises.append({"name": "Jumping Jacks", "duration": "60s", "rest": "30s"})

    plan = []
    for day in range(1, days_per_week + 1):
        plan.append(
            {
                "day": day,
                "exercises": base_exercises
            }
        )

    return plan
