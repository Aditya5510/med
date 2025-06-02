from typing import Dict, List, Any

def fetch_recipe(meal_name: str) -> Dict[str, Any]:
    """
    Stub for recipe lookup. In a real app, replace with e.g. Spoonacular API call.
    Returns a shape matching RecipeResponse:
      {
        "meal_name": str,
        "ingredients": [str, …],
        "instructions": str,
        "nutrition": { "calories": int, "protein": int, "fat": int, "carbs": int }
      }
    """
    return {
        "meal_name": meal_name,
        "ingredients": ["Ingredient A", "Ingredient B"],
        "instructions": f"Step 1: Do something with {meal_name}.",
        "nutrition": {
            "calories": 400,
            "protein": 15,
            "fat": 10,
            "carbs": 55
        }
    }
