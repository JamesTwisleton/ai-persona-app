"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { UpvoteButton } from "@/components/social/UpvoteButton";
import { ForkModal } from "@/components/social/ForkModal";
import { MessageBubble } from "@/components/conversation/MessageBubble";
import { useAuth } from "@/context/AuthContext";
import { apiFetch } from "@/lib/api";
import { Conversation, ApiError } from "@/types";

export default function PublicConversationPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [conv, setConv] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFork, setShowFork] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!id) return;
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/c/${id}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((r) => {
        if (!r.ok) throw new Error("Conversation not found");
        return r.json();
      })
      .then(setConv)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!conv || !window.confirm("Delete this conversation?")) return;
    setDeleting(true);
    try {
      await apiFetch(`/conversations/${conv.unique_id}`, { method: "DELETE" });
      window.location.href = "/conversations";
    } catch (e) {
      if (e instanceof ApiError) setError(e.message);
      setDeleting(false);
    }
  };

  if (isLoading) return <div className="flex items-center justify-center min-h-screen"><Spinner size="lg" /></div>;
  if (error || !conv) return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 px-4">
      <ErrorMessage message={error ?? "Conversation not found."} />
      <Link href="/" className="text-teal-600 hover:underline text-sm">← Back to home</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-3xl mx-auto px-4 py-10">
        <Link href="/" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 mb-4 inline-block">← Discover</Link>

        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-1">{conv.topic}</h1>
          <p className="text-sm text-gray-400 dark:text-gray-500 mb-3">
            {conv.turn_count} turns · {conv.view_count} views
            {conv.forked_from_id && (
              <> · forked from <Link href={`/c/${conv.forked_from_id}`} className="text-teal-500 hover:underline">#{conv.forked_from_id}</Link></>
            )}
          </p>

          {/* Challenge proposal */}
          {conv.is_challenge && conv.proposal && (
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-xl p-4 mb-4">
              <h3 className="text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wider mb-1">
                Challenge Proposal {conv.challenge_type ? `(${conv.challenge_type})` : ""}
              </h3>
              <p className="text-gray-900 dark:text-white font-medium italic">
                &ldquo;{conv.proposal}&rdquo;
              </p>
            </div>
          )}

          {/* Participant avatars — persuasion tracker for challenges, plain grid otherwise */}
          {conv.participants && conv.participants.length > 0 && (
            conv.is_challenge ? (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Persona Persuasion</span>
                  {(() => {
                    const persuadedCount = conv.participants!.filter(p => (p.persuaded_score ?? 0) >= 0.5).length;
                    const percent = Math.round((persuadedCount / conv.participants!.length) * 100);
                    const isSuccess = percent >= 60;
                    return (
                      <span className={`text-xs font-bold ${isSuccess ? "text-green-600" : "text-red-600"}`}>
                        Overall: {percent}% Convinced {isSuccess ? "(Success!)" : ""}
                      </span>
                    );
                  })()}
                </div>
                <div className="flex gap-4 overflow-x-auto pb-2">
                  {conv.participants.map((p, i) => {
                    const score = p.persuaded_score ?? 0;
                    const isPersuaded = score >= 0.5;
                    const statusLabel = score >= 0.7 ? "Strongly Persuaded" :
                                       score >= 0.5 ? "Persuaded" :
                                       score >= 0.3 ? "Not Persuaded" : "Strongly Against";
                    return (
                      <Link key={i} href={p.persona_unique_id ? `/p/${p.persona_unique_id}` : "#"} className="flex flex-col items-center min-w-[100px] hover:opacity-80 transition-opacity">
                        <div className={`relative w-12 h-12 rounded-full ring-2 ${isPersuaded ? "ring-green-500" : "ring-red-500"} mb-2`}>
                          {p.avatar_url ? (
                            <Image src={p.avatar_url} alt={p.persona_name ?? ""} width={48} height={48} className="w-full h-full rounded-full object-cover" unoptimized />
                          ) : (
                            <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-400 font-bold">
                              {p.persona_name?.charAt(0)}
                            </div>
                          )}
                          <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 ${isPersuaded ? "bg-green-500" : "bg-red-500"}`} />
                        </div>
                        <span className="text-[10px] font-bold text-gray-900 dark:text-white truncate w-full text-center">{p.persona_name}</span>
                        <span className={`text-[9px] font-medium ${isPersuaded ? "text-green-600" : "text-red-600"}`}>{statusLabel}</span>
                      </Link>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="flex gap-4 mb-4 flex-wrap">
                {conv.participants.map((p, i) => (
                  <Link key={i} href={p.persona_unique_id ? `/p/${p.persona_unique_id}` : "#"} className="flex flex-col items-center gap-1.5 group">
                    <div className="w-16 h-16 rounded-full overflow-hidden bg-teal-100 dark:bg-teal-900 flex items-center justify-center ring-2 ring-white dark:ring-gray-700 shadow-md">
                      {p.avatar_url ? (
                        <Image src={p.avatar_url} alt={p.persona_name ?? ""} width={64} height={64} className="object-cover w-full h-full" unoptimized />
                      ) : (
                        <span className="text-teal-700 dark:text-teal-300 font-bold text-xl">
                          {p.persona_name?.charAt(0).toUpperCase() ?? "?"}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-600 dark:text-gray-400 group-hover:text-teal-600 dark:group-hover:text-teal-400 font-medium text-center max-w-[72px] truncate">
                      {p.persona_name}
                    </span>
                  </Link>
                ))}
              </div>
            )
          )}

          <div className="flex items-center gap-2 flex-wrap">
            <UpvoteButton
              targetType="conversation"
              uniqueId={conv.unique_id}
              initialCount={conv.upvote_count}
              requiresAuth={!user}
            />

            {user ? (
              <button
                onClick={() => setShowFork(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:border-teal-400 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7h.01M12 7h.01M16 7h.01M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01" />
                </svg>
                Fork
              </button>
            ) : (
              <Link href="/login">
                <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:border-teal-400 hover:text-teal-600 dark:hover:text-teal-400 transition-colors">
                  Log in to fork
                </button>
              </Link>
            )}

            {conv.is_owner && (
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="ml-auto text-sm text-red-400 hover:text-red-600 transition-colors"
              >
                {deleting ? "Deleting…" : "Delete"}
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        {conv.messages && conv.messages.length > 0 ? (
          <div className="space-y-3">
            {(() => {
              const avatarMap = Object.fromEntries(
                (conv.participants ?? []).map((p) => [p.persona_name, p.avatar_url])
              );
              return conv.messages!.map((msg) => (
                <MessageBubble key={msg.id} message={msg} avatarUrl={avatarMap[msg.persona_name]} />
              ));
            })()}
          </div>
        ) : (
          <p className="text-center text-gray-400 dark:text-gray-500 py-12">No messages yet.</p>
        )}

        {/* Fork CTA if not logged in */}
        {!user && (
          <div className="mt-8 bg-teal-50 dark:bg-teal-900/30 rounded-xl p-5 text-center">
            <p className="text-gray-700 dark:text-gray-300 font-medium mb-3">Want to continue this conversation?</p>
            <Link href="/login">
              <button className="px-5 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors">
                Sign in to fork
              </button>
            </Link>
          </div>
        )}
      </div>

      {showFork && <ForkModal conversation={conv} onClose={() => setShowFork(false)} />}
    </div>
  );
}
