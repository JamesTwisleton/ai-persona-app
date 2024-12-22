"use client";
import React, { useState } from "react";
import Slider from "../../models/opinions/Slider";
import PersonaSlider from "./PersonaSlider";

type PersonaDescriptionProps = {
  index: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
  sliders: Slider[];
  isSelected: boolean;
  onToggleSelect: (id: number) => void;
};

const PersonaDescription = ({
  index,
  image_id,
  name,
  age,
  location,
  sliders,
  isSelected,
  onToggleSelect,
}: PersonaDescriptionProps) => {
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

      <div className="mt-5 mb-5">
        {sliders.map((slider) => (
          <PersonaSlider
            key={slider.name}
            name={slider.name}
            labelLeft={slider.labelLeft}
            labelRight={slider.labelRight}
            value={slider.value}
          />
        ))}
      </div>
    </div>
  );
};

export default PersonaDescription;
