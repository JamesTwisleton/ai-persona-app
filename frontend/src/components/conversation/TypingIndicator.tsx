"use client";

import { useState, useEffect } from "react";

interface Participant {
  persona_name: string | null;
  avatar_url?: string | null;
}

interface TypingIndicatorProps {
  participants: Participant[];
}

export function TypingIndicator({ participants }: TypingIndicatorProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (participants.length <= 1) return;

    // Cycle through participants every 3 seconds to simulate sequential "thinking"
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % participants.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [participants.length]);

  const currentParticipant = participants[currentIndex] || { persona_name: "AI" };
  const name = currentParticipant.persona_name || "AI Participant";

  return (
    <div className="flex gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 transition-opacity duration-500">
      {/* Avatar */}
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-indigo-100 dark:bg-indigo-900 overflow-hidden flex items-center justify-center transition-all duration-500">
        {currentParticipant.avatar_url ? (
          <img
            src={currentParticipant.avatar_url}
            alt={name}
            className="object-cover w-full h-full"
          />
        ) : (
          <span className="text-indigo-700 dark:text-indigo-300 font-semibold text-sm">
            {name.charAt(0).toUpperCase()}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-sm text-gray-900 dark:text-white transition-all duration-500">
            {name} is thinking
          </span>
        </div>
        <div className="flex gap-1.5 items-center h-5">
          <div className="w-2 h-2 bg-indigo-400 dark:bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="w-2 h-2 bg-indigo-400 dark:bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div className="w-2 h-2 bg-indigo-400 dark:bg-indigo-500 rounded-full animate-bounce"></div>
        </div>
      </div>
    </div>
  );
}
