"use client";
import React from "react";
import Slider from "@/models/opinions/Slider";

const PersonaSlider = ({ name, labelLeft, labelRight, value }: Slider) => {
  // Ensure the value is clamped between 0 and 1
  const clampedValue = Math.min(Math.max(value, 0), 1) * 100;

  return (
    <div className="persona-slider">
      <p className="text-center font-bold mb-2">{name}</p>
      <div className="slider-bar relative bg-gray-300 h-4 rounded-full">
        {/* Marker */}
        <div
          className="slider-marker bg-blue-500 w-6 h-6 rounded-full absolute -top-1"
          style={{ left: `calc(${clampedValue}% - 12px)` }}
        ></div>
      </div>
      <div className="flex justify-between mt-2 text-sm">
        <span>{labelLeft}</span>
        <span>{labelRight}</span>
      </div>
    </div>
  );
};

export default PersonaSlider;
