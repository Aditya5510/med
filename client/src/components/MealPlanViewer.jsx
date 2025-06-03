import React, { useEffect, useState } from "react";
import api from "../api/axiosConfig";
import { motion } from "framer-motion";

export default function MealPlanViewer() {
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .post("/health/mealplan")
      .then((res) => setPlan(res.data))
      .catch((err) =>
        setError(err.response?.data?.detail || "Failed to load meal plan")
      );
  }, []);

  if (error) {
    return <div className="text-red-600 text-center mt-8">{error}</div>;
  }
  if (!plan) {
    return <div className="text-center mt-8">Loading meal plan…</div>;
  }

  return (
    <div className="max-w-3xl mx-auto mt-8">
      <h2 className="text-2xl font-semibold mb-4 text-center">
        7-Day Meal Plan (~{plan.calorie_target} kcal/day)
      </h2>

      <div className="grid grid-cols-1 gap-6">
        {plan.days.map((dayObj) => (
          <motion.div
            key={dayObj.day}
            className="bg-white shadow rounded-lg p-4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: dayObj.day * 0.05 }}
          >
            <h3 className="text-xl font-medium mb-2">Day {dayObj.day}</h3>
            <ul className="space-y-1">
              <li>
                <span className="font-semibold">Breakfast:</span>{" "}
                {dayObj.meals.breakfast}
              </li>
              <li>
                <span className="font-semibold">Lunch:</span>{" "}
                {dayObj.meals.lunch}
              </li>
              <li>
                <span className="font-semibold">Dinner:</span>{" "}
                {dayObj.meals.dinner}
              </li>
              <li>
                <span className="font-semibold">Snacks:</span>{" "}
                {dayObj.meals.snacks}
              </li>
            </ul>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
