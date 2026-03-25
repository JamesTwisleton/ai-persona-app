"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
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
      <Link href="/" className="text-indigo-600 hover:underline text-sm">← Back to home</Link>
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
              <> · forked from <Link href={`/c/${conv.forked_from_id}`} className="text-indigo-500 hover:underline">#{conv.forked_from_id}</Link></>
            )}
          </p>

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
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7h.01M12 7h.01M16 7h.01M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01" />
                </svg>
                Fork
              </button>
            ) : (
              <Link href="/login">
                <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
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
            {conv.messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-400 dark:text-gray-500 py-12">No messages yet.</p>
        )}

        {/* Fork CTA if not logged in */}
        {!user && (
          <div className="mt-8 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl p-5 text-center">
            <p className="text-gray-700 dark:text-gray-300 font-medium mb-3">Want to continue this conversation?</p>
            <Link href="/login">
              <button className="px-5 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">
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
