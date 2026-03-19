"use client";

import { Conversation } from "@/types";
import { MessageBubble } from "./MessageBubble";
import { Button } from "@/components/ui/Button";

interface ConversationViewProps {
  conversation: Conversation;
  onContinue: () => void;
  isLoading?: boolean;
}

export function ConversationView({
  conversation,
  onContinue,
  isLoading = false,
}: ConversationViewProps) {
  const messages = conversation.messages ?? [];

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
          disabled={conversation.is_complete}
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
      </div>
    </div>
  );
}
