from typing import Literal

def calculate_bmr(
    age: int, weight: float, height: float, gender: Literal["male", "female", "other"]
) -> float:
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
       
        bmr_male = 10 * weight + 6.25 * height - 5 * age + 5
        bmr_female = 10 * weight + 6.25 * height - 5 * age - 161
        bmr = (bmr_male + bmr_female) / 2

    return float(round(bmr, 2))
