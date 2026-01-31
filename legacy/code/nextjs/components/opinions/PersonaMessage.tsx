"use client";
import React from "react";

type PersonaMessageProps = {
  index: string;
  profile_picture_filename: string;
  name: string;
  message: string;
};

const PersonaMessage = ({
  index,
  profile_picture_filename,
  name,
  message,
}: PersonaMessageProps) => {
  return (
    <div
      key={index}
      className="mt-5 mb-5 mx-5 rounded-3xl p-4 border border-gray-400 flex items-center"
    >
      {/* Left Column: Image and Name */}
      <div className="flex flex-col items-center ml-5 mr-5">
        <img
          className="h-auto max-w-full border border-gray-400 rounded-full"
          src={`/images/${profile_picture_filename}`}
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
