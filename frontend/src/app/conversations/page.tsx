"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { apiFetch } from "@/lib/api";
import { Conversation, ApiError } from "@/types";

function ConversationListItem({ conversation }: { conversation: Conversation }) {
  return (
    <Link href={`/conversations/${conversation.unique_id}`} className="block group">
      <div className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-sm transition-all">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors truncate">
              {conversation.topic}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {conversation.turn_count} / {conversation.max_turns} turns
            </p>
          </div>
          {conversation.is_complete ? (
            <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium flex-shrink-0">
              Complete
            </span>
          ) : (
            <span className="text-xs px-2 py-1 rounded-full bg-indigo-50 text-indigo-700 font-medium flex-shrink-0">
              Active
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

function ConversationsContent() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Conversation[]>("/conversations")
      .then(setConversations)
      .catch((err: ApiError) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <>
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Conversations</h1>
          <Link href="/conversations/new">
            <Button>+ New Conversation</Button>
          </Link>
        </div>

        {error && <ErrorMessage message={error} />}

        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner size="lg" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-lg mb-4">No conversations yet.</p>
            <Link href="/conversations/new">
              <Button>Start your first conversation</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {conversations.map((conv) => (
              <ConversationListItem key={conv.unique_id} conversation={conv} />
            ))}
          </div>
        )}
      </main>
    </>
  );
}

export default function ConversationsPage() {
  return (
    <AuthGuard>
      <ConversationsContent />
    </AuthGuard>
  );
}
