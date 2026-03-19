"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { OceanBar } from "@/components/persona/OceanBar";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Persona, ApiError } from "@/types";

export default function PersonaProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    apiFetch<Persona>(`/personas/${id}`)
      .then(setPersona)
      .catch((err: ApiError) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !persona) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4 px-4">
        <ErrorMessage message={error ?? "Persona not found."} />
        <Link href="/personas" className="text-indigo-600 hover:underline text-sm">
          ← Back to personas
        </Link>
      </div>
    );
  }

  const oceanScores = {
    openness: persona.ocean_openness,
    conscientiousness: persona.ocean_conscientiousness,
    extraversion: persona.ocean_extraversion,
    agreeableness: persona.ocean_agreeableness,
    neuroticism: persona.ocean_neuroticism,
  };

  const topArchetype = Object.entries(persona.archetype_affinities).reduce(
    (a, b) => (b[1] > a[1] ? b : a),
    ["", 0]
  )[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      <div className="max-w-2xl mx-auto px-4 py-10">
        <Link
          href="/personas"
          className="text-sm text-gray-500 hover:text-gray-700 mb-6 inline-block"
        >
          ← Back to personas
        </Link>

        <div className="bg-white rounded-2xl shadow-md overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-8 text-white">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-full overflow-hidden bg-white/20 flex items-center justify-center flex-shrink-0">
                {persona.avatar_url ? (
                  <Image
                    src={persona.avatar_url}
                    alt={`${persona.name} avatar`}
                    width={80}
                    height={80}
                    className="object-cover"
                    unoptimized
                  />
                ) : (
                  <span className="text-3xl font-bold text-white">
                    {persona.name.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold">{persona.name}</h1>
                <div className="flex gap-2 mt-1 flex-wrap">
                  {persona.age && (
                    <span className="text-white/80 text-sm">Age {persona.age}</span>
                  )}
                  {persona.gender && (
                    <span className="text-white/80 text-sm">· {persona.gender}</span>
                  )}
                  {persona.attitude && (
                    <span className="text-white/80 text-sm">· {persona.attitude}</span>
                  )}
                </div>
                {topArchetype && (
                  <span className="mt-2 inline-block text-xs px-2 py-0.5 rounded-full bg-white/20 text-white font-medium">
                    {topArchetype.charAt(0) + topArchetype.slice(1).toLowerCase()}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Motto */}
            {persona.motto && (
              <blockquote className="border-l-4 border-indigo-300 pl-4 italic text-gray-600 text-lg">
                &ldquo;{persona.motto}&rdquo;
              </blockquote>
            )}

            {/* Description */}
            {persona.description && (
              <div>
                <h2 className="font-semibold text-gray-700 mb-2">About</h2>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {persona.description}
                </p>
              </div>
            )}

            {/* OCEAN scores */}
            <div>
              <h2 className="font-semibold text-gray-700 mb-3">Personality Profile</h2>
              <OceanBar scores={oceanScores} />
            </div>

            {/* CTA */}
            <div className="pt-2">
              <Link href="/conversations/new">
                <button className="w-full py-3 px-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">
                  Start a Conversation
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
