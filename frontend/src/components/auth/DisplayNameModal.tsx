"use client";

import React, { useState } from "react";
import { apiFetch } from "@/lib/api";
import { User } from "@/types";

interface DisplayNameModalProps {
  isOpen: boolean;
  onSuccess: (user: User) => void;
}

export function DisplayNameModal({ isOpen, onSuccess }: DisplayNameModalProps) {
  const [displayName, setDisplayName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!displayName.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const updatedUser = await apiFetch<User>("/users/me", {
        method: "PATCH",
        body: JSON.stringify({ display_name: displayName.trim() }),
      });
      onSuccess(updatedUser);
    } catch (err: any) {
      setError(err.detail || "Failed to set display name. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4"
      data-testid="display-name-modal"
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="p-8">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
            Choose your alias
          </h2>
          <p className="text-gray-600 text-center mb-8">
            Before you start, please choose a name. This is how personas will address you in conversations. Your real name will never be leaked.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="display_name" className="block text-sm font-medium text-gray-700 mb-1">
                Display Name
              </label>
              <input
                type="text"
                id="display_name"
                data-testid="display-name-input"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all outline-none"
                placeholder="e.g. Maverick, Researcher, etc."
                required
                minLength={1}
                maxLength={50}
                autoFocus
              />
              {error && <p className="mt-2 text-sm text-red-600 font-medium">{error}</p>}
            </div>

            <button
              type="submit"
              data-testid="display-name-submit"
              disabled={isSubmitting || !displayName.trim()}
              className="w-full bg-gradient-to-r from-teal-500 to-rose-500 text-white font-bold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transform transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? "Saving..." : "Let's Go"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
