"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { ConversationView } from "@/components/conversation/ConversationView";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Conversation, ContinueConversationResponse, ApiError } from "@/types";

function ConversationContent() {
  const { id } = useParams<{ id: string }>();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isContinuing, setIsContinuing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchConversation = useCallback(async () => {
    if (!id) return;
    try {
      const data = await apiFetch<Conversation>(`/conversations/${id}`);
      setConversation(data);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    }
  }, [id]);

  useEffect(() => {
    fetchConversation().finally(() => setIsLoading(false));
  }, [fetchConversation]);

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

  return (
    <>
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-4">
          <Link href="/conversations" className="text-sm text-gray-500 hover:text-gray-700">
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
        ) : conversation ? (
          <ConversationView
            conversation={conversation}
            onContinue={handleContinue}
            onSendMessage={handleSendMessage}
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
