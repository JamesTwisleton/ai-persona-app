"use client";
import React, { useState } from "react";
import PersonaCompass from "./PersonaCompass";
import Compass from "../../models/opinions/Compass";

type PersonaDescriptionProps = {
  index: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
  compasses: Compass[];
  isSelected: boolean;
  onToggleSelect: (id: number) => void;
};

const PersonaDescription = ({
  index,
  image_id,
  name,
  age,
  location,
  compasses,
  isSelected,
  onToggleSelect,
}: PersonaDescriptionProps) => {
  const [currentCompassIndex, setCurrentCompassIndex] = useState(0);

  const handlePrevious = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCurrentCompassIndex((prevIndex) =>
      prevIndex === 0 ? compasses.length - 1 : prevIndex - 1,
    );
  };

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCurrentCompassIndex((prevIndex) =>
      prevIndex === compasses.length - 1 ? 0 : prevIndex + 1,
    );
  };

  const currentCompass = compasses[currentCompassIndex];

  const borderClasses = isSelected
    ? "border-4 border-blue-500"
    : "border border-gray-400";

  return (
    <div
      key={index}
      onClick={() => onToggleSelect(index)}
      className={`mt-5 mb-5 ml-10 mr-10 rounded-3xl p-4 cursor-pointer ${borderClasses}`}
    >
      {/* Persona Image */}
      <div className="flex justify-center items-center">
        <img
          className="h-auto max-w-full border border-gray-400 rounded-full"
          src={`/images/${image_id}`}
          style={{ width: "40%", height: "auto" }}
          alt={name}
        />
      </div>

      {/* Persona Details */}
      <div>
        <p className="text-center mt-5 mb-1 text-2xl font-normal">{name}</p>
        <p className="text-center mb-2">{age}</p>
        <p className="text-center text-gray-500">{location}</p>
      </div>

      {/* Compass with Navigation */}
      <div className="mt-5 mb-5">
        <PersonaCompass {...currentCompass} />

        {/* Navigation Arrows */}
        <div className="flex justify-center items-center mt-5 space-x-5">
          <button
            onClick={handlePrevious}
            className="px-2 py-2 rounded text-black bg-gray-300 hover:bg-gray-400 transition duration-200"
          >
            Previous
          </button>
          <button
            onClick={handleNext}
            className="px-6 py-2 rounded text-black bg-gray-300 hover:bg-gray-400 transition duration-200"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonaDescription;
