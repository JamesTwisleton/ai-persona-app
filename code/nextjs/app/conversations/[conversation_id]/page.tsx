"use client";

import DarkModeToggle from "@/components/opinions/DarkModeToggle";
import Persona from "@/models/opinions/Persona";
import PersonaMessage from "@/components/opinions/PersonaMessage";

export default async function Page({
  params,
}: {
  params: { conversation_id: string };
}) {
  const conversation_id = await params.conversation_id;

  // Example persona data
  const katie: Persona = {
    id: 1,
    image_id: "katie.png",
    name: "Katie",
    age: "27",
    location: "Romford",
    compasses: [
      {
        name: "Political Compass",
        labelLeft: "Left",
        labelRight: "Right",
        labelTop: "Authoritarian",
        labelBottom: "Libertarian",
        x: 0.15,
        y: 0.9,
      },
      {
        name: "Philosophical Compass",
        labelLeft: "Egalitarianism",
        labelRight: "Individualism",
        labelTop: "Collectivism",
        labelBottom: "Autonomy",
        x: 0.85,
        y: 0.1,
      },
    ],
  };

  const susan: Persona = {
    id: 0,
    image_id: "susan.png",
    name: "Susan",
    age: "65",
    location: "Doncaster",
    compasses: [
      {
        name: "Political Compass",
        labelLeft: "Left",
        labelRight: "Right",
        labelTop: "Authoritarian",
        labelBottom: "Libertarian",
        x: 0.6,
        y: 0.52,
      },
      {
        name: "Philosophical Compass",
        labelLeft: "Egalitarianism",
        labelRight: "Individualism",
        labelTop: "Collectivism",
        labelBottom: "Autonomy",
        x: 0.4,
        y: 0.4,
      },
    ],
  };

  const barry: Persona = {
    id: 2,
    image_id: "barry.png",
    name: "Barry",
    age: "49",
    location: "Bristol",
    compasses: [
      {
        name: "Political Compass",
        labelLeft: "Left",
        labelRight: "Right",
        labelTop: "Authoritarian",
        labelBottom: "Libertarian",
        x: 0.9,
        y: 0.2,
      },
      {
        name: "Philosophical Compass",
        labelLeft: "Egalitarianism",
        labelRight: "Individualism",
        labelTop: "Collectivism",
        labelBottom: "Autonomy",
        x: 0.1,
        y: 0.8,
      },
    ],
  };

  // TODO: use this to query get-conversation endpoint
  console.log(conversation_id);

  // example data to be replaced
  const conversation = {
    id: conversation_id,
    topic: "Cycle lanes",
    messages: [
      {
        message_id: "0",
        message:
          "Cycling is a brilliant way to get around while looking after the planet. The less cars and the more bikes the better! We should replace roads with cycle lanes.",
        persona: katie,
      },
      {
        message_id: "1",
        message:
          "I don’t have a problem with cyclists, and support green infrastructure, but I think we have enough cycle lanes as it is. Drivers need to get around too!",
        persona: susan,
      },
      {
        message_id: "2",
        message:
          "Cyclists make using the road unsafe for everyone. We should remove all existing cycle lanes and prioritise building multistory car parks.",
        persona: barry,
      },
    ],
  };

  const handleSearch = (query: string) => {};
  return (
    <div className="w-full mt-5 px-5">
      {/* Top bar (Toggle aligned to the right) */}
      <div className="flex justify-end mb-5">
        <DarkModeToggle />
      </div>

      {/* Messages Grid */}
      <div className="text-center text-2xl">
        Thoughts on "{conversation.topic}"
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 mb-10">
        {conversation.messages.map((message) => (
          <PersonaMessage
            key={message.message_id}
            index={message.message_id}
            image_id={message.persona.image_id}
            name={message.persona.name}
            message={message.message}
          />
        ))}
      </div>
    </div>
  );
}
