"use client";

import { useRef, useState, useEffect } from "react";
import Image from "next/image";
import { Conversation } from "@/types";
import { MessageBubble } from "./MessageBubble";
import { Button } from "@/components/ui/Button";

interface ConversationViewProps {
  conversation: Conversation;
  onContinue: () => void;
  onSendMessage: (text: string) => Promise<void>;
  onUpdateVisibility?: (isPublic: boolean) => Promise<void>;
  isLoading?: boolean;
}

export function ConversationView({
  conversation,
  onContinue,
  onSendMessage,
  onUpdateVisibility,
  isLoading = false,
}: ConversationViewProps) {
  const messages = conversation.messages ?? [];
  const participants = conversation.participants ?? [];
  const [inputText, setInputText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [showVisibilityModal, setShowVisibilityModal] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (bottomRef.current && typeof bottomRef.current.scrollIntoView === 'function') {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages.length]);

  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || isSending) return;
    setInputText("");
    setIsSending(true);
    try {
      await onSendMessage(text);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-col gap-4">
        {conversation.is_challenge && conversation.proposal && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-xl p-4">
            <h3 className="text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wider mb-1">
              Challenge Proposal ({conversation.challenge_type})
            </h3>
            <p className="text-gray-900 dark:text-white font-medium italic">
              &ldquo;{conversation.proposal}&rdquo;
            </p>
          </div>
        )}

        {conversation.is_challenge && participants.length > 0 && (
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Persona Persuasion
              </h3>
              <div className="text-xs font-bold">
                {(() => {
                  const persuadedCount = participants.filter(p => (p.persuaded_score ?? 0) >= 0.5).length;
                  const percent = Math.round((persuadedCount / participants.length) * 100);
                  const isSuccess = percent >= 60;
                  return (
                    <span className={isSuccess ? "text-green-600" : "text-red-600"}>
                      Overall: {percent}% Convinced {isSuccess ? "(Success!)" : ""}
                    </span>
                  );
                })()}
              </div>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {participants.map((p, i) => {
                const score = p.persuaded_score ?? 0;
                const isPersuaded = score >= 0.5;
                const statusLabel = score >= 0.7 ? "Strongly Persuaded" :
                                   score >= 0.5 ? "Persuaded" :
                                   score >= 0.3 ? "Not Persuaded" : "Strongly Against";
                return (
                  <div key={i} className="flex flex-col items-center min-w-[100px]">
                    <div className={`relative w-12 h-12 rounded-full ring-2 ${isPersuaded ? "ring-green-500" : "ring-red-500"} mb-2`}>
                      {p.avatar_url ? (
                        <img src={p.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                      ) : (
                        <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-400 font-bold">
                          {p.persona_name?.charAt(0)}
                        </div>
                      )}
                      <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 ${isPersuaded ? "bg-green-500" : "bg-red-500"}`} />
                    </div>
                    <span className="text-[10px] font-bold text-gray-900 dark:text-white truncate w-full text-center">{p.persona_name}</span>
                    <span className={`text-[9px] font-medium ${isPersuaded ? "text-green-600" : "text-red-600"}`}>{statusLabel}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">{conversation.topic}</h2>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {conversation.turn_count} / {conversation.max_turns} turns
            </span>
            {conversation.is_complete && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 font-medium">
                Complete
              </span>
            )}
            {!onUpdateVisibility && (
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {conversation.is_public ? "Public" : "Private"}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onUpdateVisibility && (
            <button
              onClick={() => setShowVisibilityModal(true)}
              className="text-sm px-3 py-1.5 rounded-md font-medium border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              {conversation.is_public ? "Make Private" : "Make Public"}
            </button>
          )}

          <Button
            onClick={onContinue}
            disabled={conversation.is_complete || isLoading || isSending}
            isLoading={isLoading}
            variant="primary"
          >
            Next Turn
          </Button>
        </div>
      </div>

      {/* Evaluation Image */}
      {conversation.image_url && (
        <div className="w-full rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 shadow-sm mb-2">
          <div className="relative aspect-video max-h-[400px] w-full">
            <Image
              src={conversation.image_url}
              alt={conversation.topic}
              fill
              className="object-contain"
              unoptimized
            />
          </div>
          <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50">
            <p className="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wider">
              Topic Image Evaluation
            </p>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="space-y-3">
        {messages.length === 0 ? (
          <p className="text-gray-400 dark:text-gray-500 text-sm italic text-center py-8">
            No messages yet — click &ldquo;Next Turn&rdquo; to start the conversation.
          </p>
        ) : (
          (() => {
            const avatarMap = Object.fromEntries(
              (conversation.participants ?? [])
                .filter((p) => p.persona_name)
                .map((p) => [p.persona_name!, p.avatar_url])
            );
            return messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                avatarUrl={avatarMap[msg.persona_name]}
              />
            ));
          })()
        )}
        <div ref={bottomRef} />
      </div>

      {showVisibilityModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowVisibilityModal(false)} aria-hidden="true" />
          <div className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
              {conversation.is_public ? "Make Conversation Private?" : "Make Conversation Public?"}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
              {conversation.is_public
                ? "This will hide the conversation from the public discovery feed. Only you will be able to see it."
                : "This will make the conversation visible on the public discovery feed. Anyone will be able to view and fork it."}
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowVisibilityModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={async () => {
                  if (onUpdateVisibility) {
                    await onUpdateVisibility(!conversation.is_public);
                  }
                  setShowVisibilityModal(false);
                }}
                className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors ${
                  conversation.is_public
                    ? "bg-gray-600 hover:bg-gray-700"
                    : "bg-indigo-600 hover:bg-indigo-700"
                }`}
              >
                {conversation.is_public ? "Make Private" : "Make Public"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User intervention input */}
      {!conversation.is_complete && (
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-2">
          <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">
            Steer the conversation — your message will be included in the next turn
          </p>
          <div className="flex gap-2 items-end">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Jump in... (Enter to send, Shift+Enter for new line)"
              rows={2}
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
            <button
              onClick={handleSend}
              disabled={!inputText.trim() || isSending}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors self-end"
            >
              {isSending ? "…" : "Send"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
