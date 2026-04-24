"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { OceanBar } from "@/components/persona/OceanBar";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { UpvoteButton } from "@/components/social/UpvoteButton";
import { AvatarGroup } from "@/components/social/AvatarGroup";
import { LoginModal } from "@/components/auth/LoginModal";
import { useAuth } from "@/context/AuthContext";
import { apiFetch } from "@/lib/api";
import { Persona, Conversation, ApiError } from "@/types";

type Sort = "hot" | "top" | "new";

const SORT_TABS: { key: Sort; label: string }[] = [
  { key: "hot", label: "Hot" },
  { key: "top", label: "Top" },
  { key: "new", label: "New" },
];

export default function PersonaProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [regenError, setRegenError] = useState<string | null>(null);
  const [loginModalOpen, setLoginModalOpen] = useState(false);

  // Conversations featuring this persona
  const [convSort, setConvSort] = useState<Sort>("hot");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [convLoading, setConvLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/p/${id}`, {
      headers: user ? { Authorization: `Bearer ${localStorage.getItem("token")}` } : {},
    })
      .then((r) => {
        if (!r.ok) throw new Error("Persona not found");
        return r.json();
      })
      .then(setPersona)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [id, user]);

  useEffect(() => {
    if (!id) return;
    setConvLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/p/${id}/conversations?sort=${convSort}`)
      .then((r) => r.json())
      .then(setConversations)
      .catch(() => setConversations([]))
      .finally(() => setConvLoading(false));
  }, [id, convSort]);

  const handleRegenerate = async () => {
    if (!persona) return;
    setRegenerating(true);
    setRegenError(null);
    try {
      const updated = await apiFetch<typeof persona>(`/personas/${persona.unique_id}/regenerate-avatar`, { method: "POST" });
      setPersona(updated);
    } catch (e) {
      if (e instanceof ApiError) setRegenError(e.message);
      else setRegenError("Avatar regeneration failed — try again.");
    } finally {
      setRegenerating(false);
    }
  };

  const handleDelete = async () => {
    if (!persona) return;
    setDeleting(true);
    try {
      await apiFetch(`/personas/${persona.unique_id}`, { method: "DELETE" });
      window.location.href = "/personas";
    } catch (e) {
      if (e instanceof ApiError) setError(e.message);
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (isLoading) return <div className="flex items-center justify-center min-h-screen"><Spinner size="lg" /></div>;
  if (error || !persona) return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 px-4">
      <ErrorMessage message={error ?? "Persona not found."} />
      <Link href="/" className="text-teal-600 hover:underline text-sm">← Back to home</Link>
    </div>
  );

  const oceanScores = {
    openness: persona.ocean_openness,
    conscientiousness: persona.ocean_conscientiousness,
    extraversion: persona.ocean_extraversion,
    agreeableness: persona.ocean_agreeableness,
    neuroticism: persona.ocean_neuroticism,
  };

  const topArchetype = Object.entries(persona.archetype_affinities).reduce(
    (a, b) => (b[1] > a[1] ? b : a), ["", 0]
  )[0];

  return (
    <>
      {showDeleteConfirm && (
        <ConfirmModal
          title={`Delete ${persona.name}?`}
          message="This will permanently delete this persona and all associated data."
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(false)}
          isLoading={deleting}
        />
      )}

      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-rose-50 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-2xl mx-auto px-4 py-10">
          <Link href="/" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 mb-6 inline-block">← Discover</Link>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md overflow-hidden">
            <div className="bg-gradient-to-r from-teal-500 to-rose-600 p-8 text-white">
              <div className="flex items-center gap-5">
                <div className="w-20 h-20 rounded-full overflow-hidden bg-white/20 flex items-center justify-center flex-shrink-0">
                  {persona.avatar_url ? (
                    <Image src={persona.avatar_url} alt={`${persona.name} avatar`} width={80} height={80} className="object-cover" unoptimized />
                  ) : (
                    <span className="text-3xl font-bold text-white">{persona.name.charAt(0).toUpperCase()}</span>
                  )}
                </div>
                <div className="flex-1">
                  <h1 className="text-3xl font-bold">{persona.name}</h1>
                  <div className="flex gap-2 mt-1 flex-wrap">
                    {persona.age && <span className="text-white/80 text-sm">Age {persona.age}</span>}
                    {persona.gender && <span className="text-white/80 text-sm">· {persona.gender}</span>}
                    {persona.attitude && <span className="text-white/80 text-sm">· {persona.attitude}</span>}
                  </div>
                  {topArchetype && (
                    <span className="mt-2 inline-block text-xs px-2 py-0.5 rounded-full bg-white/20 text-white font-medium">
                      {topArchetype.charAt(0) + topArchetype.slice(1).toLowerCase()}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Stats + upvote */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400 dark:text-gray-500">{persona.view_count} views</span>
                <UpvoteButton
                  targetType="persona"
                  uniqueId={persona.unique_id}
                  initialCount={persona.upvote_count}
                  requiresAuth={!user}
                />
              </div>

              {persona.motto && (
                <blockquote className="border-l-4 border-teal-300 pl-4 italic text-gray-600 dark:text-gray-300 text-lg">
                  &ldquo;{persona.motto}&rdquo;
                </blockquote>
              )}

              {persona.description && (
                <div>
                  <h2 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">About</h2>
                  <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">{persona.description}</p>
                </div>
              )}

              <div>
                <h2 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Personality Profile</h2>
                <OceanBar scores={oceanScores} />
              </div>

              {/* Conversations featuring this persona */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-semibold text-gray-700 dark:text-gray-300">Conversations</h2>
                  <div className="flex gap-1">
                    {SORT_TABS.map((tab) => (
                      <button
                        key={tab.key}
                        onClick={() => setConvSort(tab.key)}
                        className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                          convSort === tab.key
                            ? "bg-teal-600 text-white"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600"
                        }`}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>
                </div>
                {convLoading ? (
                  <div className="flex justify-center py-4"><Spinner /></div>
                ) : conversations.length === 0 ? (
                  <p className="text-sm text-gray-400 dark:text-gray-500 italic">No public conversations featuring this persona yet.</p>
                ) : (
                  <div className="space-y-2">
                    {conversations.map((conv) => (
                      <Link key={conv.unique_id} href={`/c/${conv.unique_id}`} className="block group">
                        <div className="border border-gray-100 dark:border-gray-700 rounded-lg p-3 hover:border-teal-200 hover:bg-teal-50/40 dark:hover:bg-teal-900/20 transition-all">
                          <p className="text-sm font-medium text-gray-800 dark:text-gray-200 group-hover:text-teal-600 dark:group-hover:text-teal-400 line-clamp-1">
                            {conv.topic}
                          </p>
                          <div className="flex items-center gap-3 mt-1.5">
                            <span className="text-xs text-gray-400 dark:text-gray-500">{conv.turn_count} turns</span>
                            {conv.participants && conv.participants.length > 0 && (
                              <AvatarGroup participants={conv.participants} size={18} />
                            )}
                            <span className="text-xs text-gray-400 dark:text-gray-500">{conv.upvote_count} upvotes</span>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              <div className="pt-2 space-y-2">
                {user ? (
                  <Link href="/conversations/new">
                    <button className="w-full py-3 px-4 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors">
                      Start a Conversation
                    </button>
                  </Link>
                ) : (
                  <button
                    onClick={() => setLoginModalOpen(true)}
                    className="w-full py-3 px-4 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors"
                  >
                    Start a Conversation
                  </button>
                )}
                {persona.is_owner && (
                  <>
                    <button
                      onClick={handleRegenerate}
                      disabled={regenerating}
                      className="w-full py-2 px-4 text-sm text-teal-600 dark:text-teal-400 hover:bg-teal-50 dark:hover:bg-teal-900/30 rounded-lg transition-colors disabled:opacity-50 border border-teal-200 dark:border-teal-700"
                    >
                      {regenerating ? "Generating new photo…" : "Regenerate profile photo"}
                    </button>
                    {regenError && (
                      <p className="text-xs text-red-500 dark:text-red-400 text-center">{regenError}</p>
                    )}
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="w-full py-2 px-4 text-sm text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                    >
                      Delete this persona
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <LoginModal
        isOpen={loginModalOpen}
        onClose={() => setLoginModalOpen(false)}
      />
    </>
  );
}
