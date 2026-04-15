"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { ConversationView } from "@/components/conversation/ConversationView";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Conversation, ContinueConversationResponse, ApiError } from "@/types";

const POLL_INTERVAL_MS = 3000;

function ConversationContent() {
  const { id } = useParams<{ id: string }>();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isContinuing, setIsContinuing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchConversation = useCallback(async () => {
    if (!id) return null;
    try {
      const data = await apiFetch<Conversation>(`/conversations/${id}`);
      setConversation(data);
      return data;
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      return null;
    }
  }, [id]);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => {
    fetchConversation().then((data) => {
      setIsLoading(false);
      if (data?.is_challenge && data?.status === "pending") {
        pollRef.current = setInterval(async () => {
          const updated = await fetchConversation();
          if (updated?.status === "active") stopPolling();
        }, POLL_INTERVAL_MS);
      }
    });
    return () => stopPolling();
  }, [fetchConversation, stopPolling]);

  const handleContinue = async () => {
    if (!id || !conversation) return;
    setError(null);
    setIsContinuing(true);
    try {
      await apiFetch<ContinueConversationResponse>(
        `/conversations/${id}/continue`,
        { method: "POST" }
      );
      await fetchConversation();
    } catch (err) {
      if (err instanceof ApiError) setError(err.detail ?? err.message);
    } finally {
      setIsContinuing(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!id) return;
    setError(null);
    try {
      await apiFetch(`/conversations/${id}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      await fetchConversation();
    } catch (err) {
      if (err instanceof ApiError) setError(err.detail ?? err.message);
    }
  };

  const handleUpdateVisibility = async (isPublic: boolean) => {
    if (!id) return;
    setError(null);
    try {
      await apiFetch(`/conversations/${id}/visibility`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_public: isPublic }),
      });
      await fetchConversation();
    } catch (err) {
      if (err instanceof ApiError) setError(err.detail ?? err.message);
    }
  };

  return (
    <>
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-4">
          <Link href="/conversations" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
            ← Back to conversations
          </Link>
        </div>

        {error && (
          <div className="mb-4">
            <ErrorMessage message={error} />
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner size="lg" />
          </div>
        ) : conversation?.is_challenge && conversation?.status === "pending" ? (
          <div className="flex flex-col items-center justify-center py-24 gap-6 text-center">
            <Spinner size="lg" />
            <div>
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-2">
                Building your challenge...
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-sm">
                Come back soon to see this challenging conversation. We&apos;re generating your personas now — this page will refresh automatically when ready.
              </p>
            </div>
          </div>
        ) : conversation ? (
          <ConversationView
            conversation={conversation}
            onContinue={handleContinue}
            onSendMessage={handleSendMessage}
            onUpdateVisibility={handleUpdateVisibility}
            isLoading={isContinuing}
          />
        ) : (
          <ErrorMessage message="Conversation not found." />
        )}
      </main>
    </>
  );
}

export default function ConversationPage() {
  return (
    <AuthGuard>
      <ConversationContent />
    </AuthGuard>
  );
}
