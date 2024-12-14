"use client";

import { useState, useEffect } from "react";
import PersonaDescription from "@/components/PersonaDescription";

export default function Page() {
  // TODO: extract this light/dark mode toggle functionality elsewhere
  const [isLightMode, setIsLightMode] = useState(false);
  // Toggle light/dark mode by updating the HTML element's class
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
    } else {
      htmlElement.classList.add("light-mode");
    }
  }, []);

  // TODO: get these values from call to flask API
  const katie = {
    index: 1,
    image_id: "katie.png",
    name: "Katie",
    age: "27",
    location: "Romford",
    x: 0.15,
    y: 0.9,
  };
  const susan = {
    index: 0,
    image_id: "susan.png",
    name: "Susan",
    age: "65",
    location: "Doncaster",
    x: 0.6,
    y: 0.52,
  };
  const barry = {
    index: 2,
    image_id: "barry.png",
    name: "Barry",
    age: "49",
    location: "Bristol",
    x: 0.9,
    y: 0.2,
  };
  const personas = [katie, susan, barry];

  return (
    <div>
      <div className="col-span-1 text-end">
        <button
          onClick={toggleDarkMode}
          className="mt-4 mb-5 mr-5 px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-700"
        >
          Toggle to {isLightMode ? "Dark" : "Light"} Mode
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 mb-10">
        {personas.map((persona) => (
          <PersonaDescription
            index={persona.index}
            image_id={persona.image_id}
            name={persona.name}
            age={persona.age}
            location={persona.location}
            x={persona.x}
            y={persona.y}
          />
        ))}
      </div>
    </div>
  );
}
