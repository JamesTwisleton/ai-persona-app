"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { AvatarGroup } from "@/components/social/AvatarGroup";
import { apiFetch } from "@/lib/api";
import { Conversation, ApiError } from "@/types";

function ConversationListItem({
  conversation,
  onDelete,
  selectMode,
  isSelected,
  onSelect,
}: {
  conversation: Conversation;
  onDelete?: (uniqueId: string) => void;
  selectMode: boolean;
  isSelected: boolean;
  onSelect?: (uniqueId: string) => void;
}) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirmDelete = async () => {
    if (!onDelete) return;
    setIsDeleting(true);
    await onDelete(conversation.unique_id);
    setIsDeleting(false);
    setShowConfirm(false);
  };

  const row = (
    <div
      className={`bg-white rounded-xl border p-4 transition-all ${
        isSelected
          ? "border-indigo-400 ring-2 ring-indigo-300"
          : "border-gray-200 hover:border-indigo-300 hover:shadow-sm"
      } ${selectMode ? "cursor-pointer" : ""}`}
      onClick={selectMode ? () => onSelect?.(conversation.unique_id) : undefined}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          {/* Select checkbox */}
          {selectMode && (
            <div
              className={`mt-0.5 w-5 h-5 flex-shrink-0 rounded border-2 flex items-center justify-center ${
                isSelected ? "bg-indigo-600 border-indigo-600" : "bg-white border-gray-300"
              }`}
            >
              {isSelected && (
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          )}

          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors truncate">
              {conversation.topic}
            </h3>
            <div className="flex items-center gap-3 mt-1.5 flex-wrap">
              <span className="text-sm text-gray-500">
                {conversation.turn_count} / {conversation.max_turns} turns
              </span>
              {conversation.participants && conversation.participants.length > 0 && (
                <AvatarGroup participants={conversation.participants} size={22} />
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {conversation.is_complete ? (
            <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium">
              Complete
            </span>
          ) : (
            <span className="text-xs px-2 py-1 rounded-full bg-indigo-50 text-indigo-700 font-medium">
              Active
            </span>
          )}
          {onDelete && !selectMode && (
            <button
              aria-label="Delete conversation"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowConfirm(true);
              }}
              className="p-1.5 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {showConfirm && (
        <ConfirmModal
          title="Delete this conversation?"
          message={`"${conversation.topic}" will be permanently deleted.`}
          confirmLabel="Delete"
          onConfirm={handleConfirmDelete}
          onCancel={() => setShowConfirm(false)}
          isLoading={isDeleting}
        />
      )}
      {selectMode ? (
        row
      ) : (
        <Link href={`/conversations/${conversation.unique_id}`} className="block group">
          {row}
        </Link>
      )}
    </>
  );
}

function ConversationsContent() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectMode, setSelectMode] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [showBulkConfirm, setShowBulkConfirm] = useState(false);
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);

  useEffect(() => {
    apiFetch<Conversation[]>("/conversations")
      .then(setConversations)
      .catch((err: ApiError) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  const handleDelete = async (uniqueId: string) => {
    try {
      await apiFetch(`/conversations/${uniqueId}`, { method: "DELETE" });
      setConversations((prev) => prev.filter((c) => c.unique_id !== uniqueId));
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
    if (selected.size === conversations.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(conversations.map((c) => c.unique_id)));
    }
  };

  const handleBulkDelete = async () => {
    setIsBulkDeleting(true);
    for (const id of Array.from(selected)) {
      try {
        await apiFetch(`/conversations/${id}`, { method: "DELETE" });
        setConversations((prev) => prev.filter((c) => c.unique_id !== id));
        setSelected((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      } catch {
        // continue
      }
    }
    setIsBulkDeleting(false);
    setShowBulkConfirm(false);
    setSelectMode(false);
  };

  return (
    <>
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6 gap-3">
          <h1 className="text-2xl font-bold text-gray-900">Conversations</h1>
          <div className="flex items-center gap-2">
            {selectMode ? (
              <>
                <button
                  onClick={toggleSelectAll}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  {selected.size === conversations.length ? "Deselect all" : "Select all"}
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
                {conversations.length > 0 && (
                  <Button variant="secondary" onClick={() => setSelectMode(true)}>
                    Select
                  </Button>
                )}
                <Link href="/conversations/new">
                  <Button>+ New Conversation</Button>
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
              <ConversationListItem
                key={conv.unique_id}
                conversation={conv}
                onDelete={handleDelete}
                selectMode={selectMode}
                isSelected={selected.has(conv.unique_id)}
                onSelect={toggleSelect}
              />
            ))}
          </div>
        )}
      </main>

      {showBulkConfirm && (
        <ConfirmModal
          title={`Delete ${selected.size} conversation${selected.size !== 1 ? "s" : ""}?`}
          message="This will permanently delete the selected conversations. This cannot be undone."
          confirmLabel={`Delete ${selected.size}`}
          onConfirm={handleBulkDelete}
          onCancel={() => setShowBulkConfirm(false)}
          isLoading={isBulkDeleting}
        />
      )}
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
