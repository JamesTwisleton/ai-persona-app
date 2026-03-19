"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Persona, PersonaCreateRequest, ApiError, Attitude } from "@/types";

const ATTITUDES: Attitude[] = ["Neutral", "Sarcastic", "Comical", "Somber"];

function PersonaForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<PersonaCreateRequest>({
    name: "",
    age: null,
    gender: null,
    description: "",
    attitude: "Neutral",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value === "" ? null : name === "age" ? parseInt(value) || null : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await apiFetch<Persona>("/personas", {
        method: "POST",
        body: JSON.stringify(form),
      });
      router.push("/personas");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail ?? err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Create Persona</h1>

        {error && (
          <div className="mb-4">
            <ErrorMessage message={error} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 bg-white rounded-xl border border-gray-200 p-6">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              value={form.name}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. Alice"
            />
          </div>

          {/* Age + Gender row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-1">
                Age
              </label>
              <input
                id="age"
                name="age"
                type="number"
                min={0}
                max={150}
                value={form.age ?? ""}
                onChange={handleChange}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g. 35"
              />
            </div>
            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-1">
                Gender
              </label>
              <input
                id="gender"
                name="gender"
                type="text"
                value={form.gender ?? ""}
                onChange={handleChange}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g. Female"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description / Backstory
            </label>
            <textarea
              id="description"
              name="description"
              rows={4}
              value={form.description ?? ""}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"
              placeholder="Describe this persona's background, job, values, personality…"
            />
            <p className="text-xs text-gray-400 mt-1">
              Claude AI will infer OCEAN personality traits from this description.
            </p>
          </div>

          {/* Attitude */}
          <div>
            <label htmlFor="attitude" className="block text-sm font-medium text-gray-700 mb-1">
              Communication Attitude
            </label>
            <select
              id="attitude"
              name="attitude"
              value={form.attitude ?? "Neutral"}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {ATTITUDES.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="submit" isLoading={isSubmitting}>
              {isSubmitting ? "Creating…" : "Create Persona"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
          </div>
        </form>
      </main>
    </>
  );
}

export default function NewPersonaPage() {
  return (
    <AuthGuard>
      <PersonaForm />
    </AuthGuard>
  );
}
