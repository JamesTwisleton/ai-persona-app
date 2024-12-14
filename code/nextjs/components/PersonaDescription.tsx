import React from "react";
import PersonaCompass from "./PersonaCompass";

type PersonaDescriptionProps = {
  index: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
  x: number;
  y: number;
};

const PersonaDescription = ({
  index,
  image_id,
  name,
  age,
  location,
  x,
  y,
}: PersonaDescriptionProps) => {
  return (
    <div
      key={index}
      className="mt-5 mb-5 ml-10 mr-10 border border-gray-400 rounded-3xl p-4"
    >
      <div className="flex justify-center items-center">
        <img
          className="h-auto max-w-full border border-gray-400 rounded-full"
          src={`/images/${image_id}`}
          style={{ width: "70%", height: "auto" }}
        />
      </div>
      <div>
        <p className="text-center mt-5 mb-1 text-3xl font-normal">{name}</p>
        <p className="text-center text-xl mb-2">{age}</p>
        <p className="text-center text-xl text-gray-500 pb-2">{location}</p>
      </div>
      <div className="mt-5 mb-5">
        <PersonaCompass x={x} y={y} />
      </div>
    </div>
  );
};

export default PersonaDescription;
