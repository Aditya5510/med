import React from "react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="text-center mt-16">
      <h2 className="text-2xl font-semibold mb-4">404 – Page Not Found</h2>
      <Link to="/" className="text-blue-600 hover:underline">
        Go back home
      </Link>
    </div>
  );
}
