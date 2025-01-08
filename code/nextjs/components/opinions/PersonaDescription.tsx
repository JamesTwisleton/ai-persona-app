"use client";
import React, { useState } from "react";
import Attribute from "../../models/opinions/Attribute";
import PersonaAttributeSlider from "./PersonaAttributeSlider";

type PersonaDescriptionProps = {
  uuid: string;
  profile_picture_filename: string;
  name: string;
  age: number;
  location: string;
  attributes: Attribute[];
  isSelected: boolean;
  onToggleSelect: (id: string) => void;
};

const PersonaDescription = ({
  uuid,
  profile_picture_filename,
  name,
  age,
  location,
  attributes,
  isSelected,
  onToggleSelect,
}: PersonaDescriptionProps) => {
  const borderClasses = isSelected
    ? "outline outline-4 outline-blue-500 border border-transparent"
    : "border border-gray-400 outline-none";

  return (
    <div
      key={uuid}
      onClick={() => onToggleSelect(uuid)}
      className={`mt-5 mb-5 ml-10 mr-10 rounded-3xl p-4 cursor-pointer ${borderClasses}`}
    >
      {/* Persona Image */}
      <div className="flex justify-center items-center">
        <img
          className="h-auto max-w-full border border-gray-400 rounded-full"
          src={`/images/${profile_picture_filename}`}
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
        <p className="text-center font-bold mb-1">Views</p>
        {attributes.map((attribute) => (
          <PersonaAttributeSlider
            key={attribute.id}
            id={attribute.id}
            name={attribute.name}
            value={attribute.value}
          />
        ))}
      </div>
    </div>
  );
};

export default PersonaDescription;
