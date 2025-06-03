import React from "react";
import MealPlanViewer from "../components/MealPlanViewer";
import WorkoutPlanViewer from "../components/WorkoutPlanViewer";

export default function PlanPage() {
  return (
    <div>
      <MealPlanViewer />
      <WorkoutPlanViewer />
    </div>
  );
}
