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
    id: 1,
    image_id: "katie.png",
    name: "Katie",
    age: "27",
    location: "Romford",
    sliders: [
      {
        name: "Political Leaning",
        labelLeft: "Left",
        labelRight: "Right",
        value: 0.15,
      },
      {
        name: "Authoritarian Leaning",
        labelLeft: "Egalitarianism",
        labelRight: "Individualism",
        value: 0.85,
      },
    ],
  };

  const susan: Persona = {
    id: 0,
    image_id: "susan.png",
    name: "Susan",
    age: "65",
    location: "Doncaster",
    sliders: [
      {
        name: "Political Leaning",
        labelLeft: "Left",
        labelRight: "Right",
        value: 0.6,
      },
      {
        name: "Authoritarian Leaning",
        labelLeft: "Egalitarianism",
        labelRight: "Individualism",
        value: 0.4,
      },
    ],
  };

  const barry: Persona = {
    id: 2,
    image_id: "barry.png",
    name: "Barry",
    age: "49",
    location: "Bristol",
    sliders: [
      {
        name: "Political Leaning",
        labelLeft: "Left",
        labelRight: "Right",
        value: 0.9,
      },
      {
        name: "Authoritarian Leaning",
        labelLeft: "Egalitarianism",
        labelRight: "Individualism",
        value: 0.1,
      },
    ],
  };

  const personas = [katie, susan, barry];
  const [selectedPersonas, setSelectedPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(false);

  const togglePersonaSelection = (id: number) => {
    setSelectedPersonas((prevSelected) => {
      const alreadySelected = prevSelected.some((p) => p.id === id);
      if (alreadySelected) {
        return prevSelected.filter((p) => p.id !== id);
      } else {
        const newPersona = personas.find((p) => p.id === id);
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
            key={persona.id}
            index={persona.id}
            image_id={persona.image_id}
            name={persona.name}
            age={persona.age}
            location={persona.location}
            sliders={persona.sliders}
            // Check if this persona is selected
            isSelected={selectedPersonas.some((p) => p.id === persona.id)}
            onToggleSelect={togglePersonaSelection}
          />
        ))}
      </div>
    </div>
  );
}
