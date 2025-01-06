import { NextResponse } from "next/server";

export async function GET() {
  const personas = [
    {
      uuid: "22eaf9",
      name: "Katie",
      age: 26,
      location: "Romford",
      profile_picture_filename: "katie.png",
      attributes: [
        { id: "13", name: "economic freedom", value: 0.3 },
        { id: "14", name: "personal freedom", value: 0.9 },
        { id: "15", name: "emotional tone", value: 0.9 },
        { id: "16", name: "cultural openness", value: 0.9 },
        { id: "17", name: "conflict intensity", value: 0.5 },
        { id: "18", name: "optimism level", value: 1.0 },
      ],
    },
    {
      uuid: "5892b1",
      name: "Susan",
      age: 68,
      location: "Doncaster",
      profile_picture_filename: "susan.png",
      attributes: [
        { id: "7", name: "economic freedom", value: 0.5 },
        { id: "8", name: "personal freedom", value: 0.5 },
        { id: "9", name: "emotional tone", value: 0.7 },
        { id: "10", name: "cultural openness", value: 0.6 },
        { id: "11", name: "conflict intensity", value: 0.4 },
        { id: "12", name: "optimism level", value: 0.7 },
      ],
    },
    {
      uuid: "5ef276",
      name: "Barry",
      age: 43,
      location: "Bristol",
      profile_picture_filename: "barry.png",
      attributes: [
        { id: "1", name: "economic freedom", value: 0.2 },
        { id: "2", name: "personal freedom", value: 0.85 },
        { id: "3", name: "emotional tone", value: 0.8 },
        { id: "4", name: "cultural openness", value: 1.0 },
        { id: "5", name: "conflict intensity", value: 0.3 },
        { id: "6", name: "optimism level", value: 1.0 },
      ],
    },
  ];

  return NextResponse.json(personas);
}
