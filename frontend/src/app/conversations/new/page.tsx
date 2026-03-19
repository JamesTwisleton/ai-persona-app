"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { apiFetch } from "@/lib/api";
import { Persona, Conversation, ConversationCreateRequest, ApiError } from "@/types";

function NewConversationForm() {
  const router = useRouter();
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isLoadingPersonas, setIsLoadingPersonas] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [topic, setTopic] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Persona[]>("/personas")
      .then(setPersonas)
      .catch(() => setError("Failed to load personas."))
      .finally(() => setIsLoadingPersonas(false));
  }, []);

  const togglePersona = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIds.size < 1) {
      setError("Select at least one persona.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const body: ConversationCreateRequest = {
        topic,
        persona_ids: Array.from(selectedIds),
      };
      const conv = await apiFetch<Conversation>("/conversations", {
        method: "POST",
        body: JSON.stringify(body),
      });
      router.push(`/conversations/${conv.unique_id}`);
    } catch (err) {
      if (err instanceof ApiError) setError(err.detail ?? err.message);
      else setError("An unexpected error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">New Conversation</h1>

        {error && (
          <div className="mb-4">
            <ErrorMessage message={error} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 bg-white rounded-xl border border-gray-200 p-6">
          {/* Topic */}
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
              Discussion Topic <span className="text-red-500">*</span>
            </label>
            <input
              id="topic"
              type="text"
              required
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. Should we colonize Mars?"
            />
          </div>

          {/* Persona selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Personas
            </label>
            {isLoadingPersonas ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : personas.length === 0 ? (
              <p className="text-sm text-gray-400 italic">
                No personas yet.{" "}
                <a href="/personas/new" className="text-indigo-600 hover:underline">
                  Create one first.
                </a>
              </p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {personas.map((persona) => (
                  <label
                    key={persona.unique_id}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedIds.has(persona.unique_id)
                        ? "border-indigo-300 bg-indigo-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.has(persona.unique_id)}
                      onChange={() => togglePersona(persona.unique_id)}
                      className="rounded text-indigo-600"
                    />
                    <div>
                      <span className="font-medium text-sm text-gray-900">
                        {persona.name}
                      </span>
                      {persona.attitude && (
                        <span className="ml-2 text-xs text-gray-400">
                          {persona.attitude}
                        </span>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            )}
            <p className="text-xs text-gray-400 mt-1">
              {selectedIds.size} selected
            </p>
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="submit" isLoading={isSubmitting} disabled={selectedIds.size === 0}>
              {isSubmitting ? "Creating…" : "Start Conversation"}
            </Button>
            <Button type="button" variant="secondary" onClick={() => router.back()}>
              Cancel
            </Button>
          </div>
        </form>
      </main>
    </>
  );
}

export default function NewConversationPage() {
  return (
    <AuthGuard>
      <NewConversationForm />
    </AuthGuard>
  );
}
