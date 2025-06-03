import React, { useState, useEffect } from "react";
import api from "../api/axiosConfig";

export default function ProfileForm() {
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("male");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");
  const [dietary, setDietary] = useState("");
  const [conditions, setConditions] = useState("");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api
      .get("/health/profile")
      .then((res) => {
        const p = res.data;
        setAge(p.age);
        setGender(p.gender);
        setWeight(p.weight);
        setHeight(p.height);
        setDietary(p.dietary_preferences.join(", "));
        setConditions(p.existing_conditions.join(", "));
      })
      .catch(() => {
        // no profile yet
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaved(false);

    const payload = {
      age: parseInt(age),
      gender,
      weight: parseFloat(weight),
      height: parseFloat(height),
      dietary_preferences: dietary
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      existing_conditions: conditions
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };

    try {
      await api.post("/health/profile", payload);
      setSaved(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Save failed");
    }
  };

  return (
    <div className="max-w-lg mx-auto mt-8 p-6 bg-white shadow-lg rounded-md">
      <h2 className="text-2xl font-semibold mb-4 text-center">
        My Health Profile
      </h2>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      {saved && <div className="text-green-600 mb-2">Profile saved!</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-gray-700">Age</label>
          <input
            type="number"
            min="1"
            className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-gray-700">Gender</label>
          <select
            className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            value={gender}
            onChange={(e) => setGender(e.target.value)}
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-gray-700">Weight (kg)</label>
          <input
            type="number"
            step="0.1"
            className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-gray-700">Height (cm)</label>
          <input
            type="number"
            step="0.1"
            className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-gray-700">
            Dietary Preferences (comma‐separated)
          </label>
          <input
            type="text"
            className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            value={dietary}
            onChange={(e) => setDietary(e.target.value)}
            placeholder="e.g. vegetarian, low‐carb"
          />
        </div>

        <div>
          <label className="block text-gray-700">
            Existing Conditions (comma‐separated)
          </label>
          <input
            type="text"
            className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            value={conditions}
            onChange={(e) => setConditions(e.target.value)}
            placeholder="e.g. knee pain, asthma"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
        >
          Save Profile
        </button>
      </form>
    </div>
  );
}
