"use client";

import { useEffect, useState } from "react";
import DarkModeToggle from "@/components/opinions/DarkModeToggle";
import Conversation from "@/models/opinions/Conversation";
import PersonaMessage from "@/components/opinions/PersonaMessage";

export default function Page({
  params,
}: {
  params: { conversation_id: string };
}) {
  const { conversation_id } = params;

  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchConversation = async () => {
      try {
        const response = await fetch(
          `/api/conversations/frontend/conversation/${conversation_id}`,
          { cache: "no-store" },
        );

        if (!response.ok) {
          throw new Error("Failed to load conversation");
        }
        const returnedJson = await response.json();
        const data: Conversation = await returnedJson.conversation;
        setConversation(data);
      } catch (error) {
        setErrorMessage((error as Error).message);
      }
    };

    fetchConversation();
  }, [conversation_id]);

  if (errorMessage) {
    return <div>Error: {errorMessage}</div>;
  }

  if (!conversation || !conversation.persona_messages) {
    return <div>Loading conversation...</div>;
  }

  return (
    <div className="w-full mt-5 px-5">
      <div className="flex justify-end mb-5">
        <DarkModeToggle />
      </div>

      <div className="text-center text-2xl">
        Thoughts on &quot;{conversation.topic}&quot;
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 mb-10">
        {conversation.persona_messages.map((persona) => (
          <PersonaMessage
            key={persona.uuid}
            index={persona.uuid}
            profile_picture_filename={persona.profile_picture_filename}
            name={persona.name}
            message={persona.messages[0]?.content || "No message content"}
          />
        ))}
      </div>
    </div>
  );
}
