"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { PersonaCard } from "@/components/persona/PersonaCard";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { apiFetch } from "@/lib/api";
import { Persona, ApiError } from "@/types";

function PersonasContent() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectMode, setSelectMode] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [showBulkConfirm, setShowBulkConfirm] = useState(false);
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);

  useEffect(() => {
    apiFetch<Persona[]>("/personas")
      .then(setPersonas)
      .catch((err: ApiError) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  const handleDelete = async (uniqueId: string) => {
    try {
      await apiFetch(`/personas/${uniqueId}`, { method: "DELETE" });
      setPersonas((prev) => prev.filter((p) => p.unique_id !== uniqueId));
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    }
  };

  const toggleSelect = (uniqueId: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(uniqueId)) next.delete(uniqueId);
      else next.add(uniqueId);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selected.size === personas.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(personas.map((p) => p.unique_id)));
    }
  };

  const handleBulkDelete = async () => {
    setIsBulkDeleting(true);
    const ids = Array.from(selected);
    for (const id of ids) {
      try {
        await apiFetch(`/personas/${id}`, { method: "DELETE" });
        setPersonas((prev) => prev.filter((p) => p.unique_id !== id));
        setSelected((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      } catch {
        // continue deleting others
      }
    }
    setIsBulkDeleting(false);
    setShowBulkConfirm(false);
    setSelectMode(false);
  };

  return (
    <>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6 gap-3">
          <h1 className="text-2xl font-bold text-gray-900">My Personas</h1>
          <div className="flex items-center gap-2">
            {selectMode ? (
              <>
                <button
                  onClick={toggleSelectAll}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  {selected.size === personas.length ? "Deselect all" : "Select all"}
                </button>
                {selected.size > 0 && (
                  <button
                    onClick={() => setShowBulkConfirm(true)}
                    className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Delete ({selected.size})
                  </button>
                )}
                <Button variant="secondary" onClick={() => { setSelectMode(false); setSelected(new Set()); }}>
                  Cancel
                </Button>
              </>
            ) : (
              <>
                {personas.length > 0 && (
                  <Button variant="secondary" onClick={() => setSelectMode(true)}>
                    Select
                  </Button>
                )}
                <Link href="/personas/new">
                  <Button>+ New Persona</Button>
                </Link>
              </>
            )}
          </div>
        </div>

        {error && <ErrorMessage message={error} />}

        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner size="lg" />
          </div>
        ) : personas.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-lg mb-4">No personas yet.</p>
            <Link href="/personas/new">
              <Button>Create your first persona</Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {personas.map((persona) => (
              <PersonaCard
                key={persona.unique_id}
                persona={persona}
                onDelete={selectMode ? undefined : handleDelete}
                selectMode={selectMode}
                isSelected={selected.has(persona.unique_id)}
                onSelect={toggleSelect}
              />
            ))}
          </div>
        )}
      </main>

      {showBulkConfirm && (
        <ConfirmModal
          title={`Delete ${selected.size} persona${selected.size !== 1 ? "s" : ""}?`}
          message="This will permanently delete the selected personas and all associated data. This cannot be undone."
          confirmLabel={`Delete ${selected.size}`}
          onConfirm={handleBulkDelete}
          onCancel={() => setShowBulkConfirm(false)}
          isLoading={isBulkDeleting}
        />
      )}
    </>
  );
}

export default function PersonasPage() {
  return (
    <AuthGuard>
      <PersonasContent />
    </AuthGuard>
  );
}
