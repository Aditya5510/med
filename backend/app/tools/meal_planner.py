from typing import List, Dict
import random

VEGETARIAN_BREAKFASTS = [
    "Oatmeal with berries", "Greek yogurt with honey", "Avocado toast", "Smoothie bowl"
]
VEGETARIAN_LUNCHES = [
    "Vegetable stir-fry with tofu", "Quinoa salad with chickpeas", "Veggie wrap", "Lentil soup"
]
VEGETARIAN_DINNERS = [
    "Grilled vegetable kebabs", "Paneer tikka with salad", "Vegetable curry with rice", "Stuffed peppers"
]
VEGETARIAN_SNACKS = [
    "Apple slices with peanut butter", "Hummus and carrot sticks", "Mixed nuts", "Fruit salad"
]

NON_VEGETARIAN_BREAKFASTS = [
    "Egg omelette with spinach", "Turkey bacon and eggs", "Greek yogurt with nuts", "Chicken sausage wrap"
]
NON_VEGETARIAN_LUNCHES = [
    "Grilled chicken salad", "Tuna sandwich", "Turkey and avocado wrap", "Chicken noodle soup"
]
NON_VEGETARIAN_DINNERS = [
    "Baked salmon with veggies", "Beef stir-fry", "Chicken curry with rice", "Shrimp pasta"
]
NON_VEGETARIAN_SNACKS = [
    "Hard-boiled egg", "Turkey jerky", "Tuna salad on crackers", "Yogurt with granola"
]

def generate_meal_plan(
    calorie_target: float, dietary_pref: List[str], days: int = 7
) -> List[Dict]:
    """
    Generate a simple weekly meal plan.

    Args:
        calorie_target: daily calorie goal (e.g., 1800)
        dietary_pref: list of dietary tags, e.g., ["vegetarian"]
        days: number of days (default 7)

    Returns:
        A list of dicts, each with keys:
          - "day": int (1..days)
          - "meals": dict with keys "breakfast", "lunch", "dinner", "snacks" (string)
    """
    plan = []
    vegetarian = "vegetarian" in [pref.lower() for pref in dietary_pref]

    for d in range(1, days + 1):
        if vegetarian:
            breakfast = random.choice(VEGETARIAN_BREAKFASTS)
            lunch = random.choice(VEGETARIAN_LUNCHES)
            dinner = random.choice(VEGETARIAN_DINNERS)
            
            snacks = random.sample(VEGETARIAN_SNACKS, k=2)
        else:
          
            breakfast = random.choice(NON_VEGETARIAN_BREAKFASTS)
            lunch = random.choice(NON_VEGETARIAN_LUNCHES)
            dinner = random.choice(NON_VEGETARIAN_DINNERS)
            snacks = random.sample(NON_VEGETARIAN_SNACKS, k=2)

        
        snacks_str = ", ".join(snacks)

        plan.append({
            "day": d,
            "meals": {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner,
                "snacks": snacks_str
            }
        })

    return plan
