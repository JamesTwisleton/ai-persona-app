"use client";

import { useState, useEffect } from "react";

export default function DarkModeToggle() {
  const [isLightMode, setIsLightMode] = useState(false);

  const toggleDarkMode = () => {
    const htmlElement = document.documentElement;

    if (isLightMode) {
      htmlElement.classList.remove("light-mode");
      htmlElement.classList.add("dark-mode");
    } else {
      htmlElement.classList.remove("dark-mode");
      htmlElement.classList.add("light-mode");
    }

    setIsLightMode(!isLightMode);
  };

  // Set initial mode based on system preference
  useEffect(() => {
    const htmlElement = document.documentElement;
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)",
    ).matches;

    if (prefersDark) {
      htmlElement.classList.add("dark-mode");
      setIsLightMode(false);
    } else {
      htmlElement.classList.add("light-mode");
      setIsLightMode(true);
    }
  }, []);

  return (
    <button
      onClick={toggleDarkMode}
      className="mt-4 mb-5 mr-5 px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-700"
    >
      Toggle to {isLightMode ? "Dark" : "Light"} Mode
    </button>
  );
}
