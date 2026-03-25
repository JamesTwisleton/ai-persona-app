import { ConversationMessage } from "@/types";

interface MessageBubbleProps {
  message: ConversationMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isFlagged = message.moderation_status === "flagged";
  const isUser = message.moderation_status === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 px-1">
        <div className="max-w-[80%]">
          <div className="flex items-center justify-end gap-2 mb-1">
            <span className="text-xs text-indigo-400">You</span>
          </div>
          <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5">
            <p className="text-sm leading-relaxed">{message.message_text}</p>
          </div>
        </div>
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center">
          <span className="text-white font-semibold text-sm">Y</span>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex gap-3 p-3 rounded-lg ${
        isFlagged ? "bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800" : "bg-gray-50 dark:bg-gray-800"
      }`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
        <span className="text-indigo-700 dark:text-indigo-300 font-semibold text-sm">
          {message.persona_name.charAt(0).toUpperCase()}
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-sm text-gray-900 dark:text-white">
            {message.persona_name}
          </span>
          <span className="text-xs text-gray-400 dark:text-gray-500">Turn {message.turn_number}</span>
          {isFlagged && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-400 font-medium">
              flagged
            </span>
          )}
        </div>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{message.message_text}</p>
      </div>
    </div>
  );
}
