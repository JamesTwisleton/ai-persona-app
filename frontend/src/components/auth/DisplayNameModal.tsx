"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { apiFetch } from "@/lib/api";
import { User } from "@/types";
import { Spinner } from "@/components/ui/Spinner";

export function DisplayNameModal() {
  const { user, login, token } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal is only visible if user is logged in but has no display name
  const isOpen = !!user && !user.display_name;

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!displayName.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      await apiFetch<User>("/users/me", {
        method: "PATCH",
        body: JSON.stringify({ display_name: displayName.trim() }),
      });

      // Refresh user state in context
      if (token) {
        await login(token);
      }
    } catch (err) {
      setError("Failed to save display name. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div data-testid="display-name-modal" className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-200">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome to PersonaComposer!
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Before you start, what should we call you? This name will be visible to others and AI personas in conversations.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="display_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Display Name
            </label>
            <input
              id="display_name"
              data-testid="display-name-input"
              type="text"
              required
              autoFocus
              className="w-full px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              placeholder="e.g. Alex, CuriousMind, etc."
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            type="submit"
            data-testid="display-name-submit"
            disabled={isLoading || !displayName.trim()}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {isLoading && <Spinner size="sm" />}
            {isLoading ? "Saving..." : "Finish Setup"}
          </button>
        </form>

        <p className="mt-4 text-xs text-gray-400 text-center">
          You can change this later in your profile settings.
        </p>
      </div>
    </div>
  );
}
