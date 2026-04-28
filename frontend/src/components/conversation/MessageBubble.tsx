import Image from "next/image";
import { ConversationMessage } from "@/types";

interface MessageBubbleProps {
  message: ConversationMessage;
  avatarUrl?: string | null;
}

export function MessageBubble({ message, avatarUrl }: MessageBubbleProps) {
  const isFlagged = message.moderation_status === "flagged";
  const isUser = message.moderation_status === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 px-1">
        <div className="max-w-[80%]">
          <div className="flex items-center justify-end gap-2 mb-1">
            <span className="text-xs text-teal-400">You</span>
          </div>
          <div className="bg-teal-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5">
            <p className="text-sm leading-relaxed">{message.message_text}</p>
          </div>
        </div>
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-teal-600 flex items-center justify-center">
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
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-teal-100 dark:bg-teal-900 overflow-hidden flex items-center justify-center">
        {avatarUrl ? (
          <Image
            src={avatarUrl}
            alt={message.persona_name}
            width={40}
            height={40}
            className="object-cover w-full h-full"
            unoptimized
          />
        ) : (
          <span className="text-teal-700 dark:text-teal-300 font-semibold text-sm">
            {message.persona_name.charAt(0).toUpperCase()}
          </span>
        )}
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

        {/* Reply to Preview */}
        {message.reply_to_id && (
          <div className="mb-2 p-2 border-l-4 border-indigo-400 bg-black/5 dark:bg-white/5 rounded-r-md">
            <div className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 mb-0.5">
              {message.reply_to_persona_name}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 italic">
              "{message.reply_to_text}"
            </div>
          </div>
        )}

        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{message.message_text}</p>
      </div>
    </div>
  );
}
