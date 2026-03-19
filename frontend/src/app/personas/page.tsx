"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { PersonaCard } from "@/components/persona/PersonaCard";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Persona, ApiError } from "@/types";

function PersonasContent() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">My Personas</h1>
          <Link href="/personas/new">
            <Button>+ New Persona</Button>
          </Link>
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {personas.map((persona) => (
              <PersonaCard
                key={persona.unique_id}
                persona={persona}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </main>
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
