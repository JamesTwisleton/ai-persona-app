"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Persona, PersonaCreateRequest, ApiError, Attitude } from "@/types";

const ATTITUDES: Attitude[] = ["Neutral", "Sarcastic", "Comical", "Somber", "Confrontational", "Blunt", "Cynical"];

const ATTITUDE_DESCRIPTIONS: Record<Attitude, string> = {
  Neutral: "Balanced and plain-spoken",
  Sarcastic: "Dry, cutting, default mode is sarcasm",
  Comical: "Finds dark or absurdist humour in everything",
  Somber: "Bleak and serious, finds optimism irritating",
  Confrontational: "Picks fights, challenges assumptions, thrives on conflict",
  Blunt: "Zero filter — says the uncomfortable thing out loud",
  Cynical: "Assumes bad faith, skewers idealism, trusts no institution",
};

function PersonaForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPublic, setIsPublic] = useState(true);
  const [ageError, setAgeError] = useState<string | null>(null);
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
    if (name === "age") {
      setAgeError(null);
      if (value === "") {
        setForm((prev) => ({ ...prev, age: null }));
        return;
      }
      if (!/^\d+$/.test(value)) {
        setAgeError("Age must be a whole number");
        return;
      }
      const n = parseInt(value, 10);
      if (n < 0 || n > 150) {
        setAgeError("Age must be between 0 and 150");
        return;
      }
      setForm((prev) => ({ ...prev, age: n }));
      return;
    }
    setForm((prev) => ({
      ...prev,
      [name]: value === "" ? null : value,
    }));
  };

  const handleAgeKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Block non-numeric keys (allow backspace, delete, arrows, tab)
    if (!/[\d]/.test(e.key) && !["Backspace", "Delete", "ArrowLeft", "ArrowRight", "Tab"].includes(e.key)) {
      e.preventDefault();
    }
  };

  const handleGenerateBackstory = async () => {
    setError(null);
    setIsGenerating(true);
    try {
      const response = await apiFetch<{ backstory: string }>("/personas/generate-backstory", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm((prev) => ({ ...prev, description: response.backstory }));
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail ?? err.message);
      } else {
        setError("Failed to generate backstory.");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (ageError) return;
    setError(null);
    setIsSubmitting(true);
    try {
      await apiFetch<Persona>("/personas", {
        method: "POST",
        body: JSON.stringify({ ...form, is_public: isPublic }),
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Create Persona</h1>

        {error && (
          <div className="mb-4">
            <ErrorMessage message={error} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              value={form.name}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="e.g. Alice"
            />
          </div>

          {/* Age + Gender row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Age
              </label>
              <input
                id="age"
                name="age"
                type="text"
                inputMode="numeric"
                value={form.age ?? ""}
                onChange={handleChange}
                onKeyDown={handleAgeKeyDown}
                className={`w-full rounded-md border px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500 ${ageError ? "border-red-400" : "border-gray-300 dark:border-gray-600"}`}
                placeholder="e.g. 35"
              />
              {ageError && <p className="text-xs text-red-500 mt-1">{ageError}</p>}
            </div>
            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Gender
              </label>
              <input
                id="gender"
                name="gender"
                type="text"
                value={form.gender ?? ""}
                onChange={handleChange}
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g. Female"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Description / Backstory
              </label>
              <button
                type="button"
                onClick={handleGenerateBackstory}
                disabled={isGenerating}
                className="text-xs font-semibold text-teal-600 dark:text-teal-400 hover:text-teal-500 dark:hover:text-teal-300 flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin h-3 w-3 text-teal-600 dark:text-teal-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Generate with AI
                  </>
                )}
              </button>
            </div>
            <textarea
              id="description"
              name="description"
              rows={4}
              value={form.description ?? ""}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-y"
              placeholder="Describe this persona's background, job, values, personality…"
            />
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              Claude AI will infer OCEAN personality traits from this description.
            </p>
          </div>

          {/* Attitude */}
          <div>
            <label htmlFor="attitude" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Communication Attitude
            </label>
            <select
              id="attitude"
              name="attitude"
              value={form.attitude ?? "Neutral"}
              onChange={handleChange}
              className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              {ATTITUDES.map((a) => (
                <option key={a} value={a}>
                  {a} — {ATTITUDE_DESCRIPTIONS[a]}
                </option>
              ))}
            </select>
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
