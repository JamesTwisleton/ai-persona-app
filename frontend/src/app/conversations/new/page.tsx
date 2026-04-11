"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { apiFetch } from "@/lib/api";
import { Persona, Conversation, ConversationCreateRequest, ApiError } from "@/types";

function PersonaPickerItem({
  persona,
  selected,
  onToggle,
}: {
  persona: Persona;
  selected: boolean;
  onToggle: () => void;
}) {
  return (
    <label
      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
        selected ? "border-teal-300 bg-teal-50 dark:bg-teal-900/30 dark:border-teal-600" : "border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500"
      }`}
    >
      <input
        type="checkbox"
        checked={selected}
        onChange={onToggle}
        className="rounded text-teal-600"
      />
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <div className="w-8 h-8 rounded-full overflow-hidden bg-teal-100 dark:bg-teal-900 flex-shrink-0 flex items-center justify-center">
          {persona.avatar_url ? (
            <Image src={persona.avatar_url} alt={persona.name} width={32} height={32} className="object-cover" unoptimized />
          ) : (
            <span className="text-teal-700 dark:text-teal-300 font-semibold text-sm">{persona.name.charAt(0)}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <span className="font-medium text-sm text-gray-900 dark:text-white truncate block">{persona.name}</span>
          {persona.attitude && (
            <span className="text-xs text-gray-400 dark:text-gray-500">{persona.attitude}</span>
          )}
        </div>
      </div>
    </label>
  );
}

function NewConversationForm() {
  const router = useRouter();
  const [myPersonas, setMyPersonas] = useState<Persona[]>([]);
  const [publicPersonas, setPublicPersonas] = useState<Persona[]>([]);
  const [isLoadingPersonas, setIsLoadingPersonas] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [topic, setTopic] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [publicSearch, setPublicSearch] = useState("");

  useEffect(() => {
    Promise.all([
      apiFetch<Persona[]>("/personas"),
      apiFetch<Persona[]>("/personas/public"),
    ])
      .then(([mine, pub]) => {
        setMyPersonas(mine);
        setPublicPersonas(pub);
      })
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

  const filteredPublic = publicPersonas.filter((p) =>
    publicSearch === "" || p.name.toLowerCase().includes(publicSearch.toLowerCase())
  );

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
        is_public: isPublic,
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">New Conversation</h1>

        {error && (
          <div className="mb-4">
            <ErrorMessage message={error} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          {/* Topic */}
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Discussion Topic <span className="text-red-500">*</span>
            </label>
            <input
              id="topic"
              type="text"
              required
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="e.g. Should we colonize Mars?"
            />
          </div>

          {/* Persona selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Personas
            </label>
            {isLoadingPersonas ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : (
              <div className="space-y-4">
                {/* My personas */}
                <div>
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                    My Personas
                  </p>
                  {myPersonas.length === 0 ? (
                    <p className="text-sm text-gray-400 dark:text-gray-500 italic">
                      No personas yet.{" "}
                      <a href="/personas/new" className="text-teal-600 dark:text-teal-400 hover:underline">
                        Create one first.
                      </a>
                    </p>
                  ) : (
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {myPersonas.map((persona) => (
                        <PersonaPickerItem
                          key={persona.unique_id}
                          persona={persona}
                          selected={selectedIds.has(persona.unique_id)}
                          onToggle={() => togglePersona(persona.unique_id)}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Public personas */}
                {publicPersonas.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                      Public Personas
                    </p>
                    <input
                      type="text"
                      value={publicSearch}
                      onChange={(e) => setPublicSearch(e.target.value)}
                      placeholder="Search by name…"
                      className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-1.5 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                    />
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {filteredPublic.map((persona) => (
                        <PersonaPickerItem
                          key={persona.unique_id}
                          persona={persona}
                          selected={selectedIds.has(persona.unique_id)}
                          onToggle={() => togglePersona(persona.unique_id)}
                        />
                      ))}
                      {filteredPublic.length === 0 && (
                        <p className="text-sm text-gray-400 dark:text-gray-500 italic">No public personas match.</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
              {selectedIds.size} selected
            </p>
          </div>

          {/* Visibility */}
          <div className="flex items-center justify-between py-1">
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Public</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Visible on the discovery feed</p>
            </div>
            <button
              type="button"
              onClick={() => setIsPublic((v) => !v)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isPublic ? "bg-teal-600" : "bg-gray-200 dark:bg-gray-600"}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isPublic ? "translate-x-6" : "translate-x-1"}`} />
            </button>
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
