"use client";
import React from "react";

type PersonaDescriptionProps = {
  index: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
};

const PersonaDescription = ({
  index,
  image_id,
  name,
  age,
  location,
}: PersonaDescriptionProps) => {
  return (
    <div
      key={index}
      className="ml-5 mr-5 border border-gray-400 rounded-3xl p-4"
    >
      <img
        className="h-auto max-w-full border border-gray-400 rounded-full"
        src={`/images/${image_id}`}
        style={{ width: "100%", height: "auto" }}
      />
      <div>
        <p className="text-center mt-5 mb-1 text-3xl font-normal">{name}</p>
        <p className="text-center text-xl mb-2">{age}</p>
        <p className="text-center text-xl text-gray-500 pb-2">{location}</p>
      </div>
    </div>
  );
};

export default PersonaDescription;
