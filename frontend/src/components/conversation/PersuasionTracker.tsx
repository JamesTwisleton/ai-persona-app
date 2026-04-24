"use client";

import Link from "next/link";

interface Participant {
  persona_id: number;
  persona_name: string | null;
  persona_unique_id: string | null;
  avatar_url?: string | null;
  persuaded_score?: number;
}

interface PersuasionTrackerProps {
  participants: Participant[];
}

export function PersuasionTracker({ participants }: PersuasionTrackerProps) {
  if (participants.length === 0) return null;

  const persuadedCount = participants.filter((p) => (p.persuaded_score ?? 0) >= 0.5).length;
  const overallPercent = Math.round((persuadedCount / participants.length) * 100);
  const isSuccess = overallPercent >= 60;

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 persuasion-tracker">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Persona Persuasion
        </h3>
        <div className="text-xs font-bold">
          <span className={isSuccess ? "text-emerald-600" : "text-rose-600"}>
            Overall: {overallPercent}% Convinced {isSuccess ? "(Success!)" : ""}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {participants.map((p, i) => {
          const score = p.persuaded_score ?? 0;

          let statusLabel = "Wavering";
          let statusColor = "bg-amber-500";
          let textColor = "text-amber-600";

          if (score < 0.35) {
            statusLabel = "Not convinced";
            statusColor = "bg-rose-500";
            textColor = "text-rose-600";
          } else if (score > 0.65) {
            statusLabel = "Persuaded";
            statusColor = "bg-emerald-500";
            textColor = "text-emerald-600";
          }

          const card = (
            <div className="flex items-center gap-3 p-2 rounded-lg bg-gray-50 dark:bg-gray-900/50 border border-gray-100 dark:border-gray-800 persona-participant">
              <div className="relative flex-shrink-0 w-10 h-10">
                {p.avatar_url ? (
                  <img src={p.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                ) : (
                  <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-400 font-bold text-sm">
                    {p.persona_name?.charAt(0)}
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-end mb-1">
                  <span className="text-xs font-bold text-gray-900 dark:text-white truncate">
                    {p.persona_name}
                  </span>
                  <span className={`text-[10px] font-bold ${textColor}`}>
                    {statusLabel}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${statusColor} rounded-full transition-all duration-500`}
                    style={{ width: `${Math.round(score * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          );

          return p.persona_unique_id ? (
            <Link key={i} href={`/p/${p.persona_unique_id}`} className="hover:opacity-90 transition-opacity">
              {card}
            </Link>
          ) : (
            <div key={i}>{card}</div>
          );
        })}
      </div>
    </div>
  );
}
