import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Menu, User, LogOut } from "lucide-react";
import { motion } from "framer-motion";
import useAuth from "../auth/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-4xl mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold text-gray-800">
          HealthPlanner
        </Link>

        <div className="flex items-center space-x-4">
          {user ? (
            <>
              <Link
                to="/profile"
                className="flex items-center text-gray-700 hover:text-blue-600"
              >
                <User className="mr-1 h-5 w-5" /> Profile
              </Link>
              <Link to="/plan" className="text-gray-700 hover:text-blue-600">
                My Plan
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center text-red-600 hover:text-red-800"
              >
                <LogOut className="mr-1 h-5 w-5" /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-blue-600">
                Login
              </Link>
              <Link
                to="/register"
                className="text-gray-700 hover:text-blue-600"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
