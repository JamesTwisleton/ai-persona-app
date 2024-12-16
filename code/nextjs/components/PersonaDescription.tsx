import React, { useState } from "react";
import PersonaCompass from "./PersonaCompass";
import Compass from "../models/Compass";

type PersonaDescriptionProps = {
  index: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
  compasses: Compass[];
};

const PersonaDescription = ({
  index,
  image_id,
  name,
  age,
  location,
  compasses,
}: PersonaDescriptionProps) => {
  const [currentCompassIndex, setCurrentCompassIndex] = useState(0);

  // Handlers for navigation
  const handlePrevious = () => {
    setCurrentCompassIndex((prevIndex) =>
      prevIndex === 0 ? compasses.length - 1 : prevIndex - 1,
    );
  };

  const handleNext = () => {
    setCurrentCompassIndex((prevIndex) =>
      prevIndex === compasses.length - 1 ? 0 : prevIndex + 1,
    );
  };

  const currentCompass = compasses[currentCompassIndex];

  return (
    <div
      key={index}
      className="mt-5 mb-5 ml-10 mr-10 border border-gray-400 rounded-3xl p-4"
    >
      {/* Persona Image */}
      <div className="flex justify-center items-center">
        <img
          className="h-auto max-w-full border border-gray-400 rounded-full"
          src={`/images/${image_id}`}
          style={{ width: "40%", height: "auto" }}
        />
      </div>

      {/* Persona Details */}
      <div>
        <p className="text-center mt-5 mb-1 text-2xl font-normal">{name}</p>
        <p className="text-center text mb-2">{age}</p>
        <p className="text-center text text-gray-500">{location}</p>
      </div>

      {/* Compass with Navigation */}
      <div className="mt-5 mb-5">
        <PersonaCompass {...currentCompass} />

        {/* Navigation Arrows */}
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={handlePrevious}
            className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
          >
            Previous
          </button>
          <button
            onClick={handleNext}
            className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonaDescription;
