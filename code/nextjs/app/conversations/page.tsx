"use client";

import { useState } from "react";
import PersonaDescription from "@/components/opinions/PersonaDescription";
import QueryBox from "@/components/opinions/QueryBox";
import DarkModeToggle from "@/components/opinions/DarkModeToggle";
import Persona from "@/models/opinions/Persona";

export default function Page() {
  // TODO: replace with call to get-personas
  // Example persona data
  const katie: Persona = {
    uuid: "22eaf9",
    name: "Katie",
    age: 26,
    location: "Romford",
    profile_picture_filename: "katie.png",
    attributes: [
      {
        id: "13",
        name: "economic",
        value: 0.3,
      },
      {
        id: "14",
        name: "freedom",
        value: 0.9,
      },
      {
        id: "15",
        name: "tone",
        value: 0.9,
      },
      {
        id: "16",
        name: "cultural",
        value: 0.9,
      },
      {
        id: "17",
        name: "conflict",
        value: 0.5,
      },
      {
        id: "18",
        name: "optimism",
        value: 1.0,
      },
    ],
  };

  const susan: Persona = {
    uuid: "5892b1",
    name: "Susan",
    age: 68,
    location: "Doncaster",
    profile_picture_filename: "susan.png",
    attributes: [
      {
        id: "7",
        name: "economic",
        value: 0.5,
      },
      {
        id: "8",
        name: "freedom",
        value: 0.5,
      },
      {
        id: "9",
        name: "tone",
        value: 0.7,
      },
      {
        id: "10",
        name: "cultural",
        value: 0.6,
      },
      {
        id: "11",
        name: "conflict",
        value: 0.4,
      },
      {
        id: "12",
        name: "optimism",
        value: 0.7,
      },
    ],
  };

  const barry: Persona = {
    uuid: "5ef276",
    name: "Barry",
    age: 43,
    location: "Bristol",
    profile_picture_filename: "barry.png",
    attributes: [
      {
        id: "1",
        name: "economic",
        value: 0.2,
      },
      {
        id: "2",
        name: "freedom",
        value: 0.85,
      },
      {
        id: "3",
        name: "tone",
        value: 0.8,
      },
      {
        id: "4",
        name: "cultural",
        value: 1.0,
      },
      {
        id: "5",
        name: "conflict",
        value: 0.3,
      },
      {
        id: "6",
        name: "optimism",
        value: 1.0,
      },
    ],
  };

  const personas = [katie, susan, barry];
  const [selectedPersonas, setSelectedPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(false);

  const togglePersonaSelection = (uuid: string) => {
    setSelectedPersonas((prevSelected) => {
      const alreadySelected = prevSelected.some((p) => p.uuid === uuid);
      if (alreadySelected) {
        return prevSelected.filter((p) => p.uuid !== uuid);
      } else {
        const newPersona = personas.find((p) => p.uuid === uuid);
        return newPersona ? [...prevSelected, newPersona] : prevSelected;
      }
    });
  };

  const handleSearch = (query: string) => {
    console.log("Search query:", query);
    console.log("Selected personas:", selectedPersonas);

    // Show a loading state
    setLoading(true);

    // Simulate an API call or processing
    setTimeout(() => {
      setLoading(false);
      alert(
        `Query: ${query}\nSelected Personas: ${selectedPersonas
          .map((p) => p.name)
          .join(", ")}`,
      );
    }, 1000);
  };

  return (
    <div>
      {/* Top bar */}
      <div className="relative w-full mt-5">
        {/* Centered Search Box */}
        <div className="flex justify-center">
          <QueryBox onSearch={handleSearch} />
        </div>

        <div className="absolute top-1/2 right-5 -translate-y-1/2">
          <DarkModeToggle />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center mt-5">
          <p className="text-xl">Loading...</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 mb-10">
        {personas.map((persona) => (
          <PersonaDescription
            key={persona.uuid}
            uuid={persona.uuid}
            profile_picture_filename={persona.profile_picture_filename}
            name={persona.name}
            age={persona.age}
            location={persona.location}
            attributes={persona.attributes}
            // Check if this persona is selected
            isSelected={selectedPersonas.some((p) => p.uuid === persona.uuid)}
            onToggleSelect={togglePersonaSelection}
          />
        ))}
      </div>
    </div>
  );
}
