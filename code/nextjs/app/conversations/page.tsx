"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation"; // or "next/router" if using the pages router
import PersonaDescription from "@/components/opinions/PersonaDescription";
import QueryBox from "@/components/opinions/QueryBox";
import DarkModeToggle from "@/components/opinions/DarkModeToggle";
import Persona from "@/models/opinions/Persona";

export default function Page() {
  const router = useRouter();
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

  const handleCreateConversation = async (topic: string) => {
    // Show loading spinner (or similar)
    setLoading(true);

    try {
      const personaUuids =
        selectedPersonas.length > 0
          ? selectedPersonas.map((p) => p.uuid)
          : personas.map((p) => p.uuid);

      const response = await fetch(
        "/api/conversations/frontend/create-conversation",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            topic,
            persona_uuids: personaUuids,
          }),
        },
      );

      if (!response.ok) {
        console.error("Failed to create conversation:", response.statusText);
        return;
      }

      // Parse the JSON response; e.g. { "conversation_uuid": "...", ... }
      const data = await response.json();

      // Redirect to /conversations/{conversation_uuid}
      router.push(`/conversation/${data.conversation_uuid}`);
    } catch (error) {
      console.error("Error creating conversation:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Top bar */}
      <div className="relative w-full mt-5">
        {/* Centered Search Box */}
        <div className="flex justify-center">
          <QueryBox onSearch={handleCreateConversation} />
        </div>

        <div className="absolute top-1/2 right-5 -translate-y-1/2">
          <DarkModeToggle />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center mt-5">
          <p className="text-xl">Loading...this will take a minute!</p>
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
            isSelected={selectedPersonas.some((p) => p.uuid === persona.uuid)}
            onToggleSelect={togglePersonaSelection}
          />
        ))}
      </div>
    </div>
  );
}
