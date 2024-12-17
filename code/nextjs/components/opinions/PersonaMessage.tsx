"use client";
import React from "react";

type PersonaMessageProps = {
  index: string;
  image_id: string;
  name: string;
  message: string;
};

const PersonaMessage = ({
  index,
  image_id,
  name,
  message,
}: PersonaMessageProps) => {
  return (
    <div
      key={index}
      className="mt-5 mb-5 mx-10 rounded-3xl p-4 border border-gray-400 flex items-center gap-4"
    >
      {/* Left Column: Image and Name */}
      <div className="flex flex-col items-center w-1/3 ml-5 mr-5">
        <img
          className="h-auto max-w-full border border-gray-400 rounded-full"
          src={`/images/${image_id}`}
          style={{ width: "100%", height: "auto" }}
          alt={name}
        />
        <p className="text-center mt-2 font-normal">{name}</p>
      </div>

      {/* Right Column: Message */}
      <div className="flex-grow">
        <p className="text-left italic">{message}</p>
      </div>
    </div>
  );
};

export default PersonaMessage;
