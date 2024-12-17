"use client";

import PersonaDescription from "@/components/PersonaDescription";
import DarkModeToggle from "@/components/DarkModeToggle";

export default function Page() {
  // TODO: get these values from call to flask API
  const katie = {
    index: 1,
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
  const susan = {
    index: 0,
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
  const barry = {
    index: 2,
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
  const personas = [katie, susan, barry];

  return (
    <div>
      <div className="col-span-1 text-end">
        <DarkModeToggle />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 mb-10">
        {personas.map((persona) => (
          <PersonaDescription
            key={persona.index}
            index={persona.index}
            image_id={persona.image_id}
            name={persona.name}
            age={persona.age}
            location={persona.location}
            compasses={persona.compasses}
          />
        ))}
      </div>
    </div>
  );
}
