"use client";

import { useState } from "react";
import { ShareModal } from "./ShareModal";

interface ShareButtonProps {
  url: string;
  title: string;
  isPublic: boolean;
  onMakePublic?: () => void;
  variant?: "icon" | "full";
}

export function ShareButton({
  url,
  title,
  isPublic,
  onMakePublic,
  variant = "full",
}: ShareButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setIsOpen(true);
        }}
        title="Share"
        className={`flex items-center gap-1.5 rounded-full text-sm font-medium transition-colors border ${
          variant === "full"
            ? "px-3 py-1.5 bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-400 dark:hover:text-indigo-400"
            : "p-1.5 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 border-transparent"
        }`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
        {variant === "full" && <span>Share</span>}
      </button>

      <ShareModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        url={url}
        title={title}
        isPublic={isPublic}
        onMakePublic={onMakePublic}
      />
    </>
  );
}
