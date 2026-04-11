"use client";

import { Persona } from "@/types";
import { OceanBar } from "./OceanBar";

interface PersonaPreviewProps {
  persona: Persona;
}

function formatArchetype(code: string): string {
  return code.charAt(0) + code.slice(1).toLowerCase();
}

export function PersonaPreview({ persona }: PersonaPreviewProps) {
  const oceanScores = {
    openness: persona.ocean_openness,
    conscientiousness: persona.ocean_conscientiousness,
    extraversion: persona.ocean_extraversion,
    agreeableness: persona.ocean_agreeableness,
    neuroticism: persona.ocean_neuroticism,
  };

  const sortedAffinities = Object.entries(persona.archetype_affinities ?? {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <div className="flex flex-col gap-4 p-4 min-w-[320px] max-w-sm">
      <div className="space-y-1.5">
        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">About</h4>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-4">
          {persona.description || "No description provided."}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Stats</h4>
          <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <p><span className="font-medium text-gray-900 dark:text-white">{persona.view_count}</span> views</p>
            <p><span className="font-medium text-gray-900 dark:text-white">{persona.upvote_count}</span> upvotes</p>
            <p><span className="font-medium text-gray-900 dark:text-white">{persona.conversation_count}</span> conversations</p>
          </div>
        </div>

        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Archetypes</h4>
          <div className="flex flex-wrap gap-1">
            {sortedAffinities.map(([code, score]) => (
              <div key={code} className="group/arch relative">
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 border border-indigo-100 dark:border-indigo-800">
                  {formatArchetype(code)}
                </span>
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-1.5 py-0.5 bg-gray-800 text-white text-[9px] rounded opacity-0 group-hover/arch:opacity-100 transition-opacity pointer-events-none whitespace-nowrap">
                  {Math.round(score * 100)}% Match
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-1.5">
        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">OCEAN Traits</h4>
        <div className="scale-90 origin-top-left -mb-4">
          <OceanBar scores={oceanScores} />
        </div>
      </div>
    </div>
  );
}
