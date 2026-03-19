import { ConversationMessage } from "@/types";

interface MessageBubbleProps {
  message: ConversationMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isFlagged = message.moderation_status === "flagged";

  return (
    <div
      className={`flex gap-3 p-3 rounded-lg ${
        isFlagged ? "bg-red-50 border border-red-200" : "bg-gray-50"
      }`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-indigo-100 flex items-center justify-center">
        <span className="text-indigo-700 font-semibold text-sm">
          {message.persona_name.charAt(0).toUpperCase()}
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-sm text-gray-900">
            {message.persona_name}
          </span>
          <span className="text-xs text-gray-400">Turn {message.turn_number}</span>
          {isFlagged && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-red-100 text-red-700 font-medium">
              flagged
            </span>
          )}
        </div>
        <p className="text-sm text-gray-700 leading-relaxed">{message.message_text}</p>
      </div>
    </div>
  );
}
