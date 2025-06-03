import React, { useEffect, useState } from "react";
import api from "../api/axiosConfig";
import { motion } from "framer-motion";

export default function WorkoutPlanViewer() {
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .post("/health/plan", { goal: "" })
      .then((res) => setPlan(res.data.workout_plan))
      .catch((err) =>
        setError(err.response?.data?.detail || "Failed to load workout plan")
      );
  }, []);

  if (error) {
    return <div className="text-red-600 text-center mt-8">{error}</div>;
  }
  if (!plan) {
    return <div className="text-center mt-8">Loading workout plan…</div>;
  }

  return (
    <div className="max-w-3xl mx-auto mt-8">
      <h2 className="text-2xl font-semibold mb-4 text-center">
        Personalized Workout Plan
      </h2>

      <div className="space-y-6">
        {plan.map((dayObj) => (
          <motion.div
            key={dayObj.day}
            className="bg-white shadow rounded-lg p-4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: dayObj.day * 0.05 }}
          >
            <h3 className="text-xl font-medium mb-2">Day {dayObj.day}</h3>
            <p className="mb-2">
              <span className="font-semibold">Warm-up:</span> {dayObj.warmup}
            </p>
            <p className="font-semibold">Exercises:</p>
            <ul className="list-disc ml-5 mb-2">
              {dayObj.exercises.map((ex, i) => (
                <li key={i}>
                  {ex.name} — {ex.sets} (rest {ex.rest})
                </li>
              ))}
            </ul>
            <p>
              <span className="font-semibold">Cool-down:</span>{" "}
              {dayObj.cooldown}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
