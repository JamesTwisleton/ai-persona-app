"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { ApiError } from "@/types";

interface UpvoteButtonProps {
  targetType: "persona" | "conversation";
  uniqueId: string;
  initialCount: number;
  initialUpvoted?: boolean;
  requiresAuth?: boolean;
}

export function UpvoteButton({
  targetType,
  uniqueId,
  initialCount,
  initialUpvoted = false,
  requiresAuth = false,
}: UpvoteButtonProps) {
  const [count, setCount] = useState(initialCount);
  const [upvoted, setUpvoted] = useState(initialUpvoted);
  const [loading, setLoading] = useState(false);

  const prefix = targetType === "persona" ? "p" : "c";

  const handleClick = async () => {
    if (requiresAuth) return;
    if (loading) return;
    setLoading(true);
    try {
      const res = await apiFetch<{ upvoted: boolean; upvote_count: number }>(
        `/${prefix}/${uniqueId}/upvote`,
        { method: "POST" }
      );
      setUpvoted(res.upvoted);
      setCount(res.upvote_count);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        window.location.href = "/login";
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading || requiresAuth}
      title={requiresAuth ? "Log in to upvote" : upvoted ? "Remove upvote" : "Upvote"}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors border ${
        upvoted
          ? "bg-indigo-600 text-white border-indigo-600"
          : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-400 dark:hover:text-indigo-400"
      } disabled:opacity-50`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-4 w-4"
        fill={upvoted ? "currentColor" : "none"}
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
        />
      </svg>
      {count}
    </button>
  );
}
