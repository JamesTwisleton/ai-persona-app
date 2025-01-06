"use client";
import React from "react";
import Attribute from "@/models/opinions/Attribute";

const PersonaAttributeSlider = ({ name, value }: Attribute) => {
  // Ensure the value is clamped between 0 and 1
  const clampedValue = Math.min(Math.max(value, 0), 1) * 100;

  return (
    <div className="persona-slider">
      <p className="text-center mb-2">{name}</p>
      <div className="slider-bar relative bg-gray-300 h-4 rounded-full mb-2">
        {/* Marker */}
        <div
          className="slider-marker bg-blue-500 w-6 h-6 rounded-full absolute -top-1"
          style={{ left: `calc(${clampedValue}% - 12px)` }}
        ></div>
      </div>
    </div>
  );
};

export default PersonaAttributeSlider;
