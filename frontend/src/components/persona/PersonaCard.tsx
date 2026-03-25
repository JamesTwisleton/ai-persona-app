"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Persona } from "@/types";
import { ConfirmModal } from "@/components/ui/ConfirmModal";

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
  isSelected?: boolean;
  onSelect?: (uniqueId: string) => void;
  selectMode?: boolean;
}

export function PersonaCard({
  persona,
  onDelete,
  isSelected = false,
  onSelect,
  selectMode = false,
}: PersonaCardProps) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const topArchetype = getTopArchetype(persona.archetype_affinities ?? {});

  const handleConfirmDelete = async () => {
    if (!onDelete) return;
    setIsDeleting(true);
    await onDelete(persona.unique_id);
    setIsDeleting(false);
    setShowConfirm(false);
  };

  const cardContent = (
    <div
      className={`bg-white dark:bg-gray-800 rounded-xl border overflow-hidden hover:shadow-md transition-all ${
        isSelected ? "border-indigo-400 ring-2 ring-indigo-300" : "border-gray-200 dark:border-gray-700 hover:border-indigo-300"
      }`}
    >
      {/* Photo-first: avatar fills top 60% */}
      <div className="relative w-full aspect-square bg-indigo-50 dark:bg-indigo-950">
        {persona.avatar_url ? (
          <Image
            src={persona.avatar_url}
            alt={`${persona.name} avatar`}
            fill
            className="object-cover"
            unoptimized
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-indigo-400 font-bold text-6xl">
              {persona.name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
        {/* Gradient overlay at bottom of photo */}
        <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/40 to-transparent" />

        {/* Select checkbox overlay */}
        {selectMode && (
          <div className="absolute top-2 left-2">
            <div
              className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                isSelected ? "bg-indigo-600 border-indigo-600" : "bg-white border-gray-300"
              }`}
            >
              {isSelected && (
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Info below photo */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-1">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm truncate">
              {persona.name}
              {persona.age && (
                <span className="ml-1 text-gray-400 dark:text-gray-500 font-normal">{persona.age}</span>
              )}
            </h3>
            {persona.motto && (
              <p className="text-xs text-gray-500 dark:text-gray-400 italic mt-0.5 line-clamp-2">
                &ldquo;{persona.motto}&rdquo;
              </p>
            )}
          </div>
          {/* Trash icon — visible when onDelete provided and not in select mode */}
          {onDelete && !selectMode && (
            <button
              aria-label={`Delete ${persona.name}`}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowConfirm(true);
              }}
              className="flex-shrink-0 p-1 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>

        <div className="flex items-center gap-1.5 mt-2 flex-wrap">
          {topArchetype && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 font-medium">
              {formatArchetype(topArchetype)}
            </span>
          )}
          {persona.attitude && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
              {persona.attitude}
            </span>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {showConfirm && (
        <ConfirmModal
          title={`Delete ${persona.name}?`}
          message="This will permanently delete this persona and all associated data. This cannot be undone."
          confirmLabel="Delete"
          onConfirm={handleConfirmDelete}
          onCancel={() => setShowConfirm(false)}
          isLoading={isDeleting}
        />
      )}

      {selectMode ? (
        <div
          className="cursor-pointer"
          onClick={() => onSelect?.(persona.unique_id)}
        >
          {cardContent}
        </div>
      ) : (
        <Link href={`/p/${persona.unique_id}`} className="block group">
          {cardContent}
        </Link>
      )}
    </>
  );
}
