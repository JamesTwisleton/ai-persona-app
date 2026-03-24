"use client";

import { useRef, useState, useEffect } from "react";
import { Conversation } from "@/types";
import { MessageBubble } from "./MessageBubble";
import { Button } from "@/components/ui/Button";

interface ConversationViewProps {
  conversation: Conversation;
  onContinue: () => void;
  onSendMessage: (text: string) => Promise<void>;
  isLoading?: boolean;
}

export function ConversationView({
  conversation,
  onContinue,
  onSendMessage,
  isLoading = false,
}: ConversationViewProps) {
  const messages = conversation.messages ?? [];
  const [inputText, setInputText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
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
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{conversation.topic}</h2>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-sm text-gray-500">
              {conversation.turn_count} / {conversation.max_turns} turns
            </span>
            {conversation.is_complete && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                Complete
              </span>
            )}
          </div>
        </div>
        <Button
          onClick={onContinue}
          disabled={conversation.is_complete || isLoading || isSending}
          isLoading={isLoading}
          variant="primary"
        >
          Next Turn
        </Button>
      </div>

      {/* Messages */}
      <div className="space-y-3">
        {messages.length === 0 ? (
          <p className="text-gray-400 text-sm italic text-center py-8">
            No messages yet — click &ldquo;Next Turn&rdquo; to start the conversation.
          </p>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* User intervention input */}
      {!conversation.is_complete && (
        <div className="border-t border-gray-200 pt-4 mt-2">
          <p className="text-xs text-gray-400 mb-2">
            Steer the conversation — your message will be included in the next turn
          </p>
          <div className="flex gap-2 items-end">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Jump in... (Enter to send, Shift+Enter for new line)"
              rows={2}
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
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
