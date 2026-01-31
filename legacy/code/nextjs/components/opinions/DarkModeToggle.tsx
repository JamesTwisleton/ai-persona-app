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
      className="rounded-l-full rounded-r-full bg-blue-500 text-white hover:bg-blue-700 transition duration-300 w-24"
    >
      {isLightMode ? "Dark" : "Light"} Mode
    </button>
  );
}
