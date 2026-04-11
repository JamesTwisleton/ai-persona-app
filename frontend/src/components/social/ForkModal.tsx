"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { Conversation, ApiError } from "@/types";

interface ForkModalProps {
  conversation: Conversation;
  onClose: () => void;
}

export function ForkModal({ conversation, onClose }: ForkModalProps) {
  const router = useRouter();
  const [topic, setTopic] = useState(conversation.topic);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFork = async () => {
    setLoading(true);
    setError(null);
    try {
      const fork = await apiFetch<Conversation>(
        `/conversations/${conversation.unique_id}/fork`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic }),
        }
      );
      router.push(`/conversations/${fork.unique_id}`);
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) {
          router.push("/login");
          return;
        }
        setError(e.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Fork conversation</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Creates a copy with the full message history. You can then continue it independently.
        </p>

        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Topic</label>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 mb-4"
        />

        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}

        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleFork}
            disabled={loading || !topic.trim()}
            className="px-4 py-2 text-sm bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50"
          >
            {loading ? "Forking…" : "Fork"}
          </button>
        </div>
      </div>
    </div>
  );
}
