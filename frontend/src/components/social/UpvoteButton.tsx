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
          ? "bg-teal-600 text-white border-teal-600"
          : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:border-teal-400 hover:text-teal-600 dark:hover:border-teal-400 dark:hover:text-teal-400"
      } disabled:opacity-50`}
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill={upvoted ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
      </svg>
      {count}
    </button>
  );
}
