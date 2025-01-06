"use client";

import { useState, useEffect } from "react";
import PersonaDescription from "@/components/opinions/PersonaDescription";
import QueryBox from "@/components/opinions/QueryBox";
import DarkModeToggle from "@/components/opinions/DarkModeToggle";
import Persona from "@/models/opinions/Persona";

export default function Page() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersonas, setSelectedPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch personas from the API
  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const response = await fetch(
          "/api/conversations/frontend/get-personas",
        );
        if (response.ok) {
          const data: Persona[] = await response.json();
          setPersonas(data);
        } else {
          console.error("Failed to fetch personas:", response.statusText);
        }
      } catch (error) {
        console.error("Error fetching personas:", error);
      }
    };

    fetchPersonas();
  }, []);

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
