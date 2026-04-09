import Image from "next/image";

interface AvatarGroupParticipant {
  persona_name: string | null;
  avatar_url?: string | null;
}

interface AvatarGroupProps {
  participants: AvatarGroupParticipant[];
  max?: number;
  size?: number;
}

export function AvatarGroup({ participants, max = 3, size = 28 }: AvatarGroupProps) {
  const shown = participants.slice(0, max);
  const overflow = participants.length - max;

  return (
    <div className="flex items-center">
      {shown.map((p, i) => (
        <div
          key={i}
          className="rounded-full border-2 border-white dark:border-gray-800 bg-teal-100 dark:bg-teal-900 overflow-hidden flex items-center justify-center flex-shrink-0"
          style={{
            width: size,
            height: size,
            marginLeft: i === 0 ? 0 : -size * 0.3,
            zIndex: shown.length - i,
          }}
          title={p.persona_name ?? ""}
        >
          {p.avatar_url ? (
            <Image
              src={p.avatar_url}
              alt={p.persona_name ?? ""}
              width={size}
              height={size}
              className="object-cover w-full h-full"
              unoptimized
            />
          ) : (
            <span
              className="text-teal-700 dark:text-teal-300 font-semibold"
              style={{ fontSize: size * 0.4 }}
            >
              {p.persona_name?.charAt(0).toUpperCase() ?? "?"}
            </span>
          )}
        </div>
      ))}
      {overflow > 0 && (
        <div
          className="rounded-full border-2 border-white dark:border-gray-800 bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0"
          style={{
            width: size,
            height: size,
            marginLeft: -size * 0.3,
            fontSize: size * 0.35,
          }}
        >
          <span className="text-gray-600 dark:text-gray-300 font-medium">+{overflow}</span>
        </div>
      )}
    </div>
  );
}
