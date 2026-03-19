import Link from "next/link";
import Image from "next/image";
import { Persona } from "@/types";

function getTopArchetype(affinities: Record<string, number>): string {
  const entries = Object.entries(affinities);
  if (entries.length === 0) return "";
  return entries.reduce((a, b) => (b[1] > a[1] ? b : a))[0];
}

function formatArchetype(code: string): string {
  return code.charAt(0) + code.slice(1).toLowerCase();
}

interface PersonaCardProps {
  persona: Persona;
  onDelete?: (uniqueId: string) => void;
}

export function PersonaCard({ persona, onDelete }: PersonaCardProps) {
  const topArchetype = getTopArchetype(persona.archetype_affinities);

  return (
    <Link href={`/p/${persona.unique_id}`} className="block group">
      <div className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-md transition-all">
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div className="flex-shrink-0 w-12 h-12 rounded-full overflow-hidden bg-indigo-100 flex items-center justify-center">
            {persona.avatar_url ? (
              <Image
                src={persona.avatar_url}
                alt={`${persona.name} avatar`}
                width={48}
                height={48}
                className="object-cover"
                unoptimized
              />
            ) : (
              <span className="text-indigo-600 font-bold text-lg">
                {persona.name.charAt(0).toUpperCase()}
              </span>
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                {persona.name}
              </h3>
              {persona.age && (
                <span className="text-sm text-gray-500">{persona.age}</span>
              )}
            </div>

            {persona.motto && (
              <p className="text-sm text-gray-600 italic mt-0.5 truncate">
                &ldquo;{persona.motto}&rdquo;
              </p>
            )}

            <div className="flex items-center gap-2 mt-2 flex-wrap">
              {topArchetype && (
                <span className="inline-flex text-xs px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-medium">
                  {formatArchetype(topArchetype)}
                </span>
              )}
              {persona.attitude && (
                <span className="inline-flex text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                  {persona.attitude}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
